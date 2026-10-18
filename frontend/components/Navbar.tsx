import Link from 'next/link';
import { useRouter } from 'next/router';
import { ArrowUpRight } from 'lucide-react';
import Logo from './Logo';
export default function Navbar() {
 const { pathname } = useRouter();
 return <header className="header"><div className="nav-wrap"><Link href="/" className="brand" aria-label="LinkGuardian home"><Logo /><span>LinkGuardian<span className="brand-ai">AI</span></span></Link><nav aria-label="Main navigation"><Link href="/" className={pathname === '/' ? 'nav-link active' : 'nav-link'} aria-current={pathname === '/' ? 'page' : undefined}>Link scanner</Link><Link href="/contact" className={pathname === '/contact' ? 'nav-link active' : 'nav-link'} aria-current={pathname === '/contact' ? 'page' : undefined}>Support <ArrowUpRight size={14}/></Link></nav><span className="nav-caption">A little caution. A safer click.</span></div></header>;
}
