
DOMAIN=command-not-found
PO_FILES := $(wildcard *.po)

all: update-po

# update the pot
$(DOMAIN).pot:
	intltool-update -p -g $(DOMAIN)

# merge the new stuff into the po files
merge-po: $(PO_FILES)
	intltool-update -r -g $(DOMAIN); 

# create mo from the pos
%.mo : %.po
	mkdir -p mo/$(subst .po,,$<)/LC_MESSAGES/ 
	msgfmt $< -o mo/$(subst .po,,$<)/LC_MESSAGES/$(DOMAIN).mo 

# dummy target 
update-po: $(DOMAIN).pot merge-po $(patsubst %.po,%.mo,$(wildcard *.po))

.PHONY: update-po

