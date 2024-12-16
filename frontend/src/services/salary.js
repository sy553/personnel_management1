import request from '../utils/request';

// 工资结构相关接口
export async function getSalaryStructures() {
  return request('/api/salary/structures');
}

export async function getSalaryStructure(id) {
  return request(`/api/salary/structures/${id}`);
}

export async function createSalaryStructure(data) {
  return request('/api/salary/structures', {
    method: 'POST',
    data,
  });
}

export async function updateSalaryStructure(id, data) {
  return request(`/api/salary/structures/${id}`, {
    method: 'PUT',
    data,
  });
}

export async function deleteSalaryStructure(id) {
  return request(`/api/salary/structures/${id}`, {
    method: 'DELETE',
  });
}

// 分配工资结构
export async function assignSalaryStructure(params) {
  return request('/api/salary/structures/assign', {
    method: 'POST',
    data: params,
  });
}

// 工资结构分配记录相关接口
export async function getSalaryStructureAssignments(params) {
  return request('/api/salary/structure-assignments', {
    params,
  });
}

export async function getSalaryStructureAssignment(id) {
  return request(`/api/salary/structure-assignments/${id}`);
}

export async function updateSalaryStructureAssignment(id, data) {
  return request(`/api/salary/structure-assignments/${id}`, {
    method: 'PUT',
    data,
  });
}

export async function deleteSalaryStructureAssignment(id) {
  return request(`/api/salary/structure-assignments/${id}`, {
    method: 'DELETE',
  });
}

// 工资记录相关接口
export async function getSalaryRecords(params) {
  return request('/api/salary/records', {
    params,
  });
}

export async function getSalaryRecord(id) {
  return request(`/api/salary/records/${id}`);
}

export async function createSalaryRecord(data) {
  return request('/api/salary/records', {
    method: 'POST',
    data,
  });
}

/**
 * 更新工资记录
 * @param {number} id - 工资记录ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 响应结果
 */
export async function updateSalaryRecord(id, data) {
  return request(`/api/salary/records/${id}`, {
    method: 'PUT',
    data,
  });
}

/**
 * 删除工资记录
 * @param {number} id - 工资记录ID
 * @returns {Promise} 响应结果
 */
export async function deleteSalaryRecord(id) {
  return request(`/api/salary/records/${id}`, {
    method: 'DELETE',
  });
}

// 批量操作接口
export async function batchCreateSalaryRecords(data) {
  return request('/api/salary/records/batch', {
    method: 'POST',
    data,
  });
}

export async function batchSendSalarySlips(data) {
  return request('/api/salary/records/batch-send-slips', {
    method: 'POST',
    data,
  });
}

// 工资条接口
export async function sendSalarySlip(id) {
  return request(`/api/salary/records/${id}/send-slip`, {
    method: 'POST',
  });
}

// 统计接口
export async function getSalaryStatistics(params) {
  return request('/api/salary/statistics', {
    params,
  });
}

// 计算接口
export async function calculateTax(data) {
  return request('/api/salary/calculate-tax', {
    method: 'POST',
    data,
  });
}

export async function calculateNetSalary(data) {
  return request('/api/salary/calculate-net', {
    method: 'POST',
    data,
  });
}
