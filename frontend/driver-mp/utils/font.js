const { STORAGE_KEYS, getItem, setItem } = require('./storage');

const SCALES = {
  standard: { key: 'standard', label: '标准', className: 'font-std' },
  large: { key: 'large', label: '大', className: 'font-lg' },
  extra: { key: 'extra', label: '特大', className: 'font-xl' }
};

function getFontScale() {
  const key = getItem(STORAGE_KEYS.FONT_SCALE, 'large');
  return SCALES[key] || SCALES.large;
}

function setFontScale(key) {
  const next = SCALES[key] ? key : 'large';
  setItem(STORAGE_KEYS.FONT_SCALE, next);
  return SCALES[next];
}

module.exports = {
  SCALES,
  getFontScale,
  setFontScale
};
