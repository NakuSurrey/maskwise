// static export - `next build` writes plain HTML/CSS/JS to out/, no Node server at runtime
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  // every page folder gets its own index.html so nginx can serve clean URLs
  trailingSlash: true,
  // static export cannot use Next's image optimizer at request time - turn it off
  images: { unoptimized: true },
};
module.exports = nextConfig;
