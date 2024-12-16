/**
 * 薪资管理模块的工具函数
 */

import moment from 'moment';

/**
 * 格式化金额显示
 * @param {number} amount - 金额数值
 * @param {number} decimals - 小数位数，默认2位
 * @returns {string} 格式化后的金额字符串
 */
export const formatAmount = (amount, decimals = 2) => {
  if (typeof amount !== 'number') return '¥0.00';
  return `¥${amount.toFixed(decimals)}`;
};

/**
 * 计算工资总额
 * @param {Object} record - 工资记录对象
 * @returns {number} 工资总额
 */
export const calculateTotalSalary = (record) => {
  const {
    basic_salary = 0,
    allowances = 0,
    overtime_pay = 0,
    bonus = 0,
  } = record;
  return basic_salary + allowances + overtime_pay + bonus;
};

/**
 * 获取发放状态显示文本
 * @param {string} status - 状态代码
 * @returns {string} 状态显示文本
 */
export const getPaymentStatusText = (status) => {
  const statusMap = {
    pending: '待发放',
    paid: '已发放',
    cancelled: '已取消',
  };
  return statusMap[status] || status;
};

/**
 * 获取发放状态标签颜色
 * @param {string} status - 状态代码
 * @returns {string} 标签颜色
 */
export const getPaymentStatusColor = (status) => {
  const colorMap = {
    pending: 'orange',
    paid: 'green',
    cancelled: 'red',
  };
  return colorMap[status] || 'default';
};

/**
 * 格式化日期显示
 * @param {string|Date} date - 日期对象或字符串
 * @param {string} format - 格式化模式，默认YYYY-MM-DD
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (date, format = 'YYYY-MM-DD') => {
  if (!date) return '';
  return moment(date).format(format);
};

/**
 * 计算统计数据
 * @param {Array} records - 工资记录数组
 * @returns {Object} 统计结果
 */
export const calculateStatistics = (records) => {
  if (!Array.isArray(records)) return {};
  
  const total_records = records.length;
  const total_amount = records.reduce((sum, record) => sum + (record.net_salary || 0), 0);
  const pending_count = records.filter(r => r.payment_status === 'pending').length;
  const paid_count = records.filter(r => r.payment_status === 'paid').length;
  const average_salary = total_records ? total_amount / total_records : 0;

  return {
    total_records,
    total_amount,
    pending_count,
    paid_count,
    average_salary,
  };
};

/**
 * 验证工资记录数据
 * @param {Object} record - 工资记录对象
 * @returns {boolean} 是否有效
 */
export const validateSalaryRecord = (record) => {
  const requiredFields = [
    'employee_id',
    'year',
    'month',
    'basic_salary',
  ];
  
  return requiredFields.every(field => {
    const value = record[field];
    return value !== undefined && value !== null && value !== '';
  });
};

/**
 * 生成工资条导出数据
 * @param {Object} record - 工资记录对象
 * @returns {Object} 导出数据对象
 */
export const generateSalarySlipData = (record) => {
  const {
    employee,
    year,
    month,
    basic_salary,
    allowances,
    overtime_pay,
    bonus,
    tax,
    net_salary,
  } = record;

  return {
    员工姓名: employee?.name || '',
    部门: employee?.department_name || '',
    年份: year,
    月份: month,
    基本工资: formatAmount(basic_salary),
    补贴: formatAmount(allowances),
    加班费: formatAmount(overtime_pay),
    奖金: formatAmount(bonus),
    个税: formatAmount(tax),
    实发工资: formatAmount(net_salary),
  };
};
