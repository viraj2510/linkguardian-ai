import type { AppProps } from 'next/app';
import Head from 'next/head';
import '../styles/globals.css';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
export default function App({ Component, pageProps }: AppProps) {
  return <><Head><link rel="icon" type="image/svg+xml" href="/favicon.svg" /><title>LinkGuardian AI | Think before you click</title><meta name="description" content="Check suspicious links with URL pattern analysis and DNS validation." /><meta name="viewport" content="width=device-width, initial-scale=1" /></Head><div className="app-shell"><a className="skip-link" href="#main">Skip to content</a><Navbar /><main id="main"><Component {...pageProps} /></main><Footer /></div></>;
}
