#!/bin/sh
# Oswald Bold, the storefront's display face. Both build scripts convert it to
# outlines, so it is only needed to rebuild the marks — not to use them.
# Not committed: it is an OFL font, and fetching beats vendoring a binary plus
# its licence into a repo that otherwise holds no binaries.
set -e
url=$(curl -sS "https://fonts.googleapis.com/css2?family=Oswald:wght@700" \
      | sed -n 's/.*src: url(\([^)]*\)).*/\1/p')
curl -sSL -o "$(dirname "$0")/Oswald-Bold.ttf" "$url"
echo "Oswald-Bold.ttf $(wc -c < "$(dirname "$0")/Oswald-Bold.ttf") bytes"
