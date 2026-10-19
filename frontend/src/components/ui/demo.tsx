import { TiltedGridHero } from "@/components/ui/tilted-grid-hero";

// Curated high-resolution Unsplash stock imagery (hardware, products, aesthetics, and gradients)
const IMAGES = [
  {
    src: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
    alt: "Apple MacBook Air on minimal desk",
  },
  {
    src: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80",
    alt: "Retro technology neon glowing hardware setup",
  },
  {
    src: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
    alt: "Sony noise-canceling headphones studio shot",
  },
  {
    src: "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
    alt: "Futuristic printed circuit board electronic macro",
  },
  {
    src: "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
    alt: "Ergonomic gaming mouse on dark surface",
  },
  {
    src: "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80",
    alt: "Smartphone with high-resolution edge-to-edge display",
  },
  {
    src: "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=800&q=80",
    alt: "Wireless earbuds in magnetic charging case",
  },
  {
    src: "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=800&q=80",
    alt: "Minimalist workspace hardware accessories",
  },
  {
    src: "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=800&q=80",
    alt: "Flagship AMOLED smartphone with stylus",
  },
  {
    src: "https://images.unsplash.com/photo-1609592426038-f94ca2376991?auto=format&fit=crop&w=800&q=80",
    alt: "High-capacity digital fast charging power bank",
  },
];

export default function TiltedGridHeroDemo() {
  return (
    <TiltedGridHero
      images={IMAGES}
      className="h-[560px] w-full rounded-lg border border-border bg-background"
    >
      <div className="relative z-10 flex h-full flex-col items-center justify-between py-12 text-center">
        <div className="px-6">
          <h1 className="text-balance text-4xl font-medium tracking-tight text-foreground sm:text-5xl">
            Every frame,
            <br />
            brought into focus.
          </h1>
        </div>
        <p className="max-w-md text-balance px-6 text-sm text-muted-foreground">
          Images curve in from one edge, flatten out at the centre, then fade
          away round the other.
        </p>
      </div>
    </TiltedGridHero>
  );
}

export { TiltedGridHeroDemo };
