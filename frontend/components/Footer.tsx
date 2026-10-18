import Link from 'next/link';
import Logo from './Logo';
export default function Footer() { return <footer className="footer"><div><span className="footer-brand"><Logo className="footer-logo"/> LinkGuardian AI</span><span>Built by Viraj Gundewar</span></div><div><span>© {new Date().getFullYear()} LinkGuardian</span><Link href="/contact">Questions or a false positive? Get in touch →</Link></div></footer>; }
