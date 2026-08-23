const ICONS = {
  home: '/assets/icons/svg/home.svg',
  task: '/assets/icons/svg/task.svg',
  wallet: '/assets/icons/svg/wallet.svg',
  finance: '/assets/icons/svg/wallet.svg',
  user: '/assets/icons/svg/user.svg',
  profile: '/assets/icons/svg/user.svg',
  bell: '/assets/icons/svg/bell.svg',
  camera: '/assets/icons/svg/camera.svg',
  warn: '/assets/icons/svg/warn.svg',
  fuel: '/assets/icons/svg/fuel.svg',
  chart: '/assets/icons/svg/chart.svg',
  card: '/assets/icons/svg/card.svg',
  truck: '/assets/icons/svg/truck.svg',
  'truck-side': '/assets/icons/svg/truck-side.svg',
  star: '/assets/icons/svg/star.svg',
  settings: '/assets/icons/svg/settings.svg',
  info: '/assets/icons/svg/info.svg',
  building: '/assets/icons/svg/building.svg',
  check: '/assets/icons/svg/check.svg',
  clock: '/assets/icons/svg/clock.svg',
  file: '/assets/icons/svg/file.svg',
  phone: '/assets/icons/svg/phone.svg',
  nav: '/assets/icons/svg/nav.svg',
  pin: '/assets/icons/svg/pin.svg',
  wrench: '/assets/icons/svg/wrench.svg',
  box: '/assets/icons/svg/box.svg',
  more: '/assets/icons/svg/more.svg'
};

Component({
  properties: {
    name: { type: String, value: '' },
    size: { type: String, value: 'md' },
    color: { type: String, value: '' }
  },
  data: { src: '' },
  observers: {
    name(name) {
      this.setData({ src: ICONS[name] || '' });
    }
  }
});
