#!/bin/bash

ZINSTANCE=~/Plone/zinstance
I18NDUDE=$ZINSTANCE/bin/i18ndude
PLONE_POT=$ZINSTANCE/parts/omelette/plone/app/locales/locales/plone.pot
BIKA_POT=$ZINSTANCE/src/bika.lims/bika/lims/locales/bika.pot

# tx pull -a

# Flush the english (transifex source language) po files
# If we don't do this, new *-manual translations won't be synced.

> en/LC_MESSAGES/plone.po
> en/LC_MESSAGES/bika.po
> en/LC_MESSAGES/bika.health.po

# Remove generated files

find . -name "*.mo" -delete
rm plone.pot 2>/dev/null
rm bika.pot 2>/dev/null
rm bika.health.pot 2>/dev/null

### plone domain (overrides)
touch i18ndude.pot
#$I18NDUDE rebuild-pot --pot i18ndude.pot --exclude "build" --create plone ../profiles/
msgcat --strict --use-first plone-manual.pot i18ndude.pot $PLONE_POT > plone.pot
$I18NDUDE sync --pot plone.pot */LC_MESSAGES/plone.po
rm i18ndude.pot

### bika domain (overrides)
touch i18ndude.pot
#$I18NDUDE rebuild-pot --pot i18ndude.pot --exclude "build" --create bika ../profiles/
msgcat --strict --use-first bika-manual.pot i18ndude.pot $BIKA_POT > bika.pot
$I18NDUDE sync --pot bika.pot */LC_MESSAGES/bika.po
rm i18ndude.pot

### bika.health domain
touch i18ndude.pot
$I18NDUDE rebuild-pot --pot i18ndude.pot --exclude "build" --create bika.health ..
msgcat --strict --use-first bika.health-manual.pot i18ndude.pot > bika.health.pot
$I18NDUDE sync --pot bika.health.pot */LC_MESSAGES/bika.health.po
rm i18ndude.pot

# Compile *.mo

for po in `find . -name "*.po"`; do msgfmt -o ${po/%po/mo} $po; done

# tx push -s -t
