const MOCK_ENABLED = false;

const notifySettings = {
  approval: true,
  alert: true,
  status: false
};

function customerCopy(task) {
  const no = (task && (task.taskNo || task.waybillNo)) || '';
  const dest = (task && task.destination) || '目的地';
  const plate = (task && task.plateNumber) || '运输车辆';
  return `您好，${no} 目前在途，车牌 ${plate}，预计运往 ${dest}。如需最新位置请稍后，我们会再同步。`;
}

module.exports = {
  MOCK_ENABLED,
  notifySettings,
  customerCopy
};
