/** Isotipo de marca (compás/plano). Único origen del SVG, reutilizado por Logo y estados vacíos. */
export function BrandMark({ size = 18, className = "" }: { size?: number; className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <circle cx="12" cy="6" r="2.4" />
      <path d="M10 7.6 5.5 19M14 7.6 18.5 19M8 15h8" />
    </svg>
  );
}
