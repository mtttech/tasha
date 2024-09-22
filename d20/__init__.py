from typing import Any, Dict

from . import (
    alignments,
    backgrounds,
    classes,
    feats,
    languages,
    lineages,
    multiclasses,
    proficiencies,
    skills,
    species,
    spells,
    subclasses,
)

srd5e: Dict[str, Any] = dict()
srd5e.update(alignments.alignments)
srd5e.update(backgrounds.backgrounds)
srd5e.update(classes.classes)
srd5e.update(feats.feats)
srd5e.update(languages.languages)
srd5e.update(lineages.lineages)
srd5e.update(multiclasses.multiclasses)
srd5e.update(proficiencies.proficiencies)
srd5e.update(species.species)
srd5e.update(skills.skills)
srd5e.update(spells.spells)
srd5e.update(subclasses.subclasses)
