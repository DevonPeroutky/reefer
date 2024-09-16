# How to run

## Prerequisites
You'll need to have [pixi](https://pixi.sh/latest/) installed. You can do so with `curl -fsSL https://pixi.sh/install.sh | bash`. You'll also need an Anthropic API key set as an environment variable as `ANTHROPIC_API_KEY=sk-...`

## Install and Run
```
# Only need to do this once
pixi install

# Run
pixi shell

# Runs on 8000
uvicorn app.app:app --reload
```

# Some Helpful information
Built using [fastht.ml](https://fastht.ml/). The general principles revolves around agent, the agent's state, and tasks. The agent runs pre-defined tasks, the tasks receive the current agent state and perform their action, and then update the agent state.


# TO-DO

# Milestone 1 - Demo-able 
- [x] Figure out how to do [modal w/chunked transfer](https://discord.com/channels/689892369998676007/1247700012952191049/1282255144913866823)
- [ ] REFACTOR?
- [ ] Test finding contacts E2E
  - [ ] Iterate on the relevant keywords being parsed
  - [x] Update ContactsTableIcon success on complete
- [ ] Generate outreach
  - [ ] Skeleton out action dropdown w/checklist items
  - [ ] Implement find emails for selected contacts

## Issues
- [ ] LinkedIn shares no relevant data with SERP results
- [ ] Certain companies have custom/unique openings page (once they get big enough)
  - [ ] Snap, Meta, etc, have their own portal
- [ ] Handle pagination
  - [ ] Anduril, Datadog have a giant paginated list --> Handle pagination

# Milestone 2 - Persistence
- [ ] Persist results to Database
  - [ ] Companies
  - [ ] Job Openings
  - [ ] Contacts
- [ ] Results Page


# Milestone 3 - Personalize
- [ ] Take in resume/work/background information
- [ ] Generate personalized outreach based on resume/work/background

# Betterments
- [ ] When looking for contacts, we're currently just going based on who at the company is relevant to the job, when the user's network is also a huge resource.
