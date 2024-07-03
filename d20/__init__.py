from typing import Any, Dict

from . import (
    alignments,
    classes,
    languages,
    metrics,
    proficiencies,
    sizes,
    skills,
    spells,
    types,
)

srd5e: Dict[str, Any] = dict()
srd5e.update(alignments.alignments)
srd5e.update(classes.classes)
srd5e.update(languages.languages)
srd5e.update(metrics.metrics)
srd5e.update(proficiencies.proficiencies)
srd5e.update(sizes.sizes)
srd5e.update(skills.skills)
srd5e.update(spells.spells)
srd5e.update(types.types)
