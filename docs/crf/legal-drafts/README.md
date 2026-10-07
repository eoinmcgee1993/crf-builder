# Legal drafts — deliberately outside the publish root

`public/` is the Vercel publish root. Anything in it is served. These three
files were in it, so `/privacy` and `/terms` were live, serving their own
editorial note — "Before publishing: replace [LEGAL ENTITY NAME],
[REGISTERED ADDRESS] and [CONTACT EMAIL]" — above a data-controller line that
was literally those brackets. A privacy policy with blanks in it is worse than
no policy: it is a public document that fails at the only job it has.

They live here instead. The rule is now enforced by where the files are rather
than by anyone remembering a deploy checklist.

## Publishing them

Four facts have to exist first:

1. The registered legal entity name
2. The registered address
3. A contact email on a domain you control
4. The governing law

Then, in one commit: fill all three files in, `git mv` them back into
`public/`, and restore the `Privacy` / `Terms` footer links — each of the six
storefront pages has a comment marking where they came out. Links and files go
back together; a footer link to a 404 and a published policy full of
placeholders are two ways to fail the same check.

`next.config.mjs` already carries the `/privacy` and `/terms` rewrites, so no
routing change is needed.
