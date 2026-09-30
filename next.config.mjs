/** @type {import('next').NextConfig} */

// The six storefront pages are plain HTML in public/ and are the live site.
// The Next app around them is the rebuild, page by page, and is not serving
// anything customer-facing yet.
//
// These rewrites keep the URLs the storefront already uses — /apparel, /ecu,
// /mods, /approve, /desk and / — so links already in the wild keep working
// through the cutover. They are `beforeFiles` because / has to reach
// public/index.html rather than app/page.tsx; an ordinary rewrite loses to the
// filesystem and the placeholder would win.
//
// To cut a page over: build it in the app router, delete its line here, and
// delete its file from public/. One page at a time, and nothing else moves.
const STATIC_PAGES = ["apparel", "ecu", "mods", "approve", "desk", "sprockets", "privacy", "terms"];

const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return {
      beforeFiles: [
        { source: "/", destination: "/index.html" },
        ...STATIC_PAGES.map((p) => ({
          source: `/${p}`,
          destination: `/${p}.html`,
        })),
      ],
    };
  },
  async headers() {
    // The operator page is unlinked and carries its own noindex meta tag. This
    // covers both the extensionless route and the file itself.
    const noindex = [{ key: "X-Robots-Tag", value: "noindex, nofollow" }];
    return [
      { source: "/desk", headers: noindex },
      { source: "/desk.html", headers: noindex },
    ];
  },
};

export default nextConfig;
