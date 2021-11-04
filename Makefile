DEV_ENV := ./dev-env
PYTHON_VERSION := 3.10

.PHONY: help
help:  ## Show help
	@IFS=$$'\n' ; \
    help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/:.*##/##/'`); \
    for help_line in $${help_lines[@]}; do \
        IFS=$$'#' ; \
        help_split=($$help_line) ; \
        help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
        help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
        printf "%-20s %s\n" $$help_command $$help_info ; \
    done



##
## > Development environment
.PHONY: create-env
create-env: $(DEV_ENV)  ## Create development environment
$(DEV_ENV):
	@conda create -y -p $(DEV_ENV) python==$(PYTHON_VERSION) && \
	source activate $(DEV_ENV) && \
	pip install -r requirements.txt && \
	pip install -r requirements-dev.txt && \
	pre-commit install

.PHONY: delete-env
delete-env: ## Delete development environment
	@rm -rf $(DEV_ENV)

.PHONY: recreate-env
recreate-env: delete-env create-env ## Recreate development environment
