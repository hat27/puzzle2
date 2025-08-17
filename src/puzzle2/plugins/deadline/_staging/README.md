This folder holds new Deadline plugin scaffold files staged for review.

To deploy:
- Copy plugins/puzzle2/puzzle2.py to your repository's custom plugin path.
- Copy _staging/PluginPreLoad.py to plugins/puzzle2/PluginPreLoad.py in the repository.
- Copy _staging/puzzle2.param to plugins/puzzle2/puzzle2.param in the repository.
- (Optional) Copy scripts/Submission/SubmitPuzzle2Deadline.py to Repository/scripts/Submission.

Notes:
- The plugin overlays addon-built command with Application Plugin executable when available.
- PUZZLE_JOB_PATH is set to the generated config.json for batch_kicker.
