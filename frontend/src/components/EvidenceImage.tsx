import { useState } from 'react';

interface EvidenceImageProps {
  image: { thumbnail_url: string; secure_url: string };
  alt: string;
  className?: string;
}

/** A failed thumbnail transformation must not hide the original evidence. */
export function EvidenceImage({ image, alt, className }: EvidenceImageProps) {
  const [failedUrl, setFailedUrl] = useState('');
  const thumbnail = image.thumbnail_url || image.secure_url;
  const src = failedUrl === thumbnail ? image.secure_url : thumbnail;
  if (!src || failedUrl === image.secure_url) {
    return <span role="img" aria-label={`${alt} (preview unavailable)`} className={className}>Preview unavailable</span>;
  }
  return <img src={src} alt={alt} className={className} loading="lazy" onError={() => setFailedUrl(src)} />;
}
