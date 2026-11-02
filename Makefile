PREFIX ?= /usr/local
DESTDIR ?=
APPDIR = $(DESTDIR)$(PREFIX)/share/orbitz-youtube-wrapper
.PHONY: install test
install:
	install -d "$(APPDIR)/app" "$(APPDIR)/i18n"
	install -d "$(APPDIR)/app/fonts"
	install -m644 app/fonts/*.ttf "$(APPDIR)/app/fonts/"
	install -d "$(APPDIR)/app/audio"
	install -m644 app/audio/*.ogg "$(APPDIR)/app/audio/"
	install -m644 app/*.py app/*.js app/index.html "$(APPDIR)/app/"
	install -m644 VERSION "$(APPDIR)/VERSION"
	install -m644 i18n/*.py i18n/*.json "$(APPDIR)/i18n/"
	install -Dm755 data/orbitz-youtube-wrapper "$(DESTDIR)$(PREFIX)/bin/orbitz-youtube-wrapper"
	install -Dm644 data/io.orbitz.YouTubeDesktop.desktop "$(DESTDIR)$(PREFIX)/share/applications/io.orbitz.YouTubeDesktop.desktop"
	install -Dm644 app/youtube.svg "$(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/io.orbitz.YouTubeDesktop.svg"
	install -Dm644 data/io.orbitz.YouTubeDesktop.metainfo.xml "$(DESTDIR)$(PREFIX)/share/metainfo/io.orbitz.YouTubeDesktop.metainfo.xml"
	install -Dm644 data/io.orbitz.YouTubeDesktop.gschema.xml "$(DESTDIR)$(PREFIX)/share/glib-2.0/schemas/io.orbitz.YouTubeDesktop.gschema.xml"
	install -Dm644 LICENSE "$(DESTDIR)$(PREFIX)/share/licenses/orbitz-youtube-wrapper/LICENSE"
	install -Dm644 THIRD_PARTY_NOTICES.md "$(DESTDIR)$(PREFIX)/share/licenses/orbitz-youtube-wrapper/THIRD_PARTY_NOTICES.md"
	install -m644 data/licenses/*.txt "$(DESTDIR)$(PREFIX)/share/licenses/orbitz-youtube-wrapper/"
	glib-compile-schemas "$(DESTDIR)$(PREFIX)/share/glib-2.0/schemas"
test:
	GSETTINGS_BACKEND=memory python3 -m unittest discover -s tests -v
	@set -e; for test in tests/test_youtube_*.js; do node "$$test"; done
