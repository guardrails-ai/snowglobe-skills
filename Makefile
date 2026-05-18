SKILLS_DIR := plugins/snowglobe-skills/skills
CLAUDE_SKILLS_DIR := $(HOME)/.claude/skills

SKILLS := $(notdir $(wildcard $(SKILLS_DIR)/*))

.PHONY: mount unmount

mount:
	@mkdir -p $(CLAUDE_SKILLS_DIR)
	@for skill in $(SKILLS); do \
		ln -sfn "$(CURDIR)/$(SKILLS_DIR)/$$skill" "$(CLAUDE_SKILLS_DIR)/$$skill" && \
		echo "mounted $$skill"; \
	done

unmount:
	@for skill in $(SKILLS); do \
		if [ -L "$(CLAUDE_SKILLS_DIR)/$$skill" ]; then \
			rm "$(CLAUDE_SKILLS_DIR)/$$skill" && echo "unmounted $$skill"; \
		fi \
	done
