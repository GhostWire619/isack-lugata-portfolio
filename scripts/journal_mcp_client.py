"""Connect with the official MCP SDK and optionally create a reviewable draft.

Install scripts/requirements-mcp.txt in a separate environment. Credentials are
read from a private file, never placed in command arguments or printed.
"""
import argparse
import asyncio
import json
from pathlib import Path
from urllib.parse import urlsplit

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main(options):
    url = urlsplit(options.url)
    if url.scheme != 'https' and not (url.scheme == 'http' and url.hostname in {'localhost', '127.0.0.1', '::1'}):
        raise ValueError('Use HTTPS, or HTTP on localhost for development.')
    credential = json.loads(Path(options.token_file).read_text(encoding='utf-8'))
    async with streamablehttp_client(options.url, headers={'Authorization': 'Bearer ' + credential['token']}) as (read, write, _):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            print(f'Connected: {initialized.serverInfo.name}, MCP {initialized.protocolVersion}')
            tools = await session.list_tools()
            print('Tools: ' + ', '.join(tool.name for tool in tools.tools))
            if options.article_file:
                arguments = json.loads(Path(options.article_file).read_text(encoding='utf-8'))
                images = {}
                for item in options.image_file:
                    import base64
                    key, filename = item.split('=', 1)
                    payload = {'title': Path(filename).stem.replace('-', ' '),
                        'image_base64': base64.b64encode(Path(filename).read_bytes()).decode('ascii')}
                    upload = await session.call_tool('upload_image', payload)
                    if upload.isError:
                        raise RuntimeError(upload.content[0].text)
                    image = upload.structuredContent or json.loads(upload.content[0].text)
                    images[key] = image['image_id']
                    print(f"Uploaded {key}: image #{image['image_id']}")
                if isinstance(arguments.get('cover_image_id'), str):
                    arguments['cover_image_id'] = images[arguments['cover_image_id'].removeprefix('@')]
                for section in arguments.get('sections', []):
                    if section['type'] == 'image' and isinstance(section.get('image_id'), str):
                        section['image_id'] = images[section['image_id'].removeprefix('@')]
                result = await session.call_tool('create_article_draft', arguments)
                if result.isError:
                    raise RuntimeError(result.content[0].text)
                created = result.structuredContent or json.loads(result.content[0].text)
                retry = await session.call_tool('create_article_draft', arguments)
                retried = retry.structuredContent or json.loads(retry.content[0].text)
                assert not retry.isError and retried['reused']
                assert created['article']['id'] == retried['article']['id']
                readback = await session.call_tool('get_article', {'article_id': created['article']['id']})
                saved = readback.structuredContent or json.loads(readback.content[0].text)
                assert not readback.isError and saved['article']['title'] == arguments['title']
                assert not saved['article']['live']
                print(json.dumps({'article_id': saved['article']['id'], 'title': saved['article']['title'],
                    'editor_url': saved['article']['editor_url'], 'status': 'draft', 'retry_verified': True}, indent=2))
                if options.result_file:
                    Path(options.result_file).write_text(json.dumps(saved, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://localhost:8001/mcp/')
    parser.add_argument('--token-file', required=True)
    parser.add_argument('--article-file', help='JSON draft arguments. Omit to only connect and list tools.')
    parser.add_argument('--result-file', help='Optional JSON readback output file.')
    parser.add_argument('--image-file', action='append', default=[], help='KEY=PATH to upload via MCP; use @KEY for image IDs in the article JSON.')
    asyncio.run(main(parser.parse_args()))
