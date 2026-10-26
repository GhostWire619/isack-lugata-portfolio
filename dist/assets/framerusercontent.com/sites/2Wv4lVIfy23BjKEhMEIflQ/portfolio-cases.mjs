import{o as jsx,l as jsxs,N as Fragment,v as useEffect}from"./react.DUE-xjOD.mjs?v=c25ce90af72b00eb";
import{ut as useRouter}from"./framer.DCW-Gja5.mjs?v=c25ce90af72b00eb";
const routes={"/": "UTNT6GAXH", "/about": "XdYBo4_p8", "/ecofy": "OJvd1BNaN", "/osher-market": "IhYkVKpYR", "/wakili-msomi": "boFkVS3RZ", "/falco": "Zmwx4Ibvc", "/habitek": "mld1MIphZ", "/tanstack-tanzania": "wi2Xaghpb", "/globoexpats": "kuKUydbQG"};
export function makeCasePage(markup, original) {
 function CasePage(props) {
  const router=useRouter();
  useEffect(()=>{document.dispatchEvent(new Event('portfolio:route'));},[]);
  function onClick(event) {
   if(event.defaultPrevented || event.button!==0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)return;
   const a=event.target.closest('a');
   if(!a || a.target==='_blank' || a.hasAttribute('download'))return;
   const url=new URL(a.href,location.href);
   const route=routes[url.pathname.replace(/\/$/,'') || '/'];
   if(url.origin!==location.origin || !route || url.hash)return;
   event.preventDefault();
   router.navigate(route,undefined,{});
  }
  return jsxs(Fragment,{children:[jsx('style',{'data-framer-html-style':'',dangerouslySetInnerHTML:{__html:'html body { background: rgb(255, 255, 255); }'}}),jsx('div',{className:'portfolio-case-root','data-framer-root':'',style:props.style,onClick,dangerouslySetInnerHTML:{__html:markup}}),jsx('div',{id:'overlay'})]});
 }
 Object.assign(CasePage,original);
 CasePage.displayName='PortfolioCasePage';
 return CasePage;
}
