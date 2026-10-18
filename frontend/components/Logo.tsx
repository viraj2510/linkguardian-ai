export default function Logo({ className = '' }: { className?: string }) {
 return <img src="/linkguardian-logo.svg" width={40} height={40} alt="" aria-hidden="true" className={`guardian-logo ${className}`} />;
}
