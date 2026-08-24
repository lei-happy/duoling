const PERSONA_OPTIONS = [
  { value: 'dispatch', label: '调度' },
  { value: 'boss', label: '老板' },
  { value: 'finance', label: '财务' },
  { value: 'captain', label: '车队长' }
];

const PERSONA_LABELS = PERSONA_OPTIONS.reduce((acc, item) => {
  acc[item.value] = item.label;
  return acc;
}, {});

function personaLabel(value) {
  return PERSONA_LABELS[value] || '';
}

function resolvePersona(user) {
  const personas = (user && user.personas) || [];
  const preferred =
    user && user.workplaceConfig && user.workplaceConfig.defaultPersona;
  if (preferred && personas.indexOf(preferred) >= 0) {
    return preferred;
  }
  return personas[0] || '';
}

module.exports = {
  PERSONA_OPTIONS,
  PERSONA_LABELS,
  personaLabel,
  resolvePersona
};
