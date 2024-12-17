import request from '../utils/request';
import moment from 'moment';
import { getDepartments } from './department';
import { getPositions } from './position';

// 员工相关API
/**
 * 创建新员工
 * @param {Object} data - 员工信息
 * @returns {Promise} 返回创建结果
 */
export async function createEmployee(data) {
  try {
    console.log('Creating employee with data:', data);
    const response = await request.post('/api/employees', data);
    console.log('Create employee response:', response);
    return response;
  } catch (error) {
    console.error('Create employee error:', error);
    throw error;
  }
}

/**
 * 更新员工信息
 * @param {number} id - 员工ID
 * @param {Object} data - 更新的员工信息
 * @returns {Promise} 返回更新结果
 */
export async function updateEmployee(id, data) {
  // 确保所有日期字段格式正确
  const formattedData = {
    ...data,
    birth_date: data.birth_date || null,
    hire_date: data.hire_date || null,
    resignation_date: data.resignation_date || null,
    photo_url: data.photo_url || null,
    contract_url: data.contract_url || null,
    department_id: data.department_id || null,
    position_id: data.position_id || null,
    employment_status: data.employment_status || 'active',
  };

  console.log('Updating employee:', id);
  console.log('Update data:', formattedData);
  
  try {
    const response = await request.put(`/api/employees/${id}`, formattedData);
    console.log('Update response:', response);
    return response;
  } catch (error) {
    console.error('Update error:', error);
    throw error;
  }
}

/**
 * 删除员工
 * @param {number} id - 员工ID
 * @returns {Promise} 返回删除结果
 */
export async function deleteEmployee(id) {
  return request.delete(`/api/employees/${id}`);
}

/**
 * 获取单个员工信息
 * @param {number} id - 员工ID
 * @returns {Promise} 返回员工信息
 */
export async function getEmployee(id) {
  return request.get(`/api/employees/${id}`);
}

/**
 * 获取员工列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回员工列表和分页信息
 */
export async function getEmployees(params = {}) {
  try {
    const response = await request.get('/api/employees', { params });
    return response;
  } catch (error) {
    console.error('Get employees error:', error);
    throw error;
  }
}

/**
 * 获取员工列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {number} params.department_id - 部门ID筛选
 * @param {number} params.position_id - 职位ID筛选
 * @returns {Promise} 返回员工列表和分页信息
 */
// export async function getEmployees(params) {
//   try {
//     console.log('Fetching employees with params:', params);
//     const response = await request.get('/api/employees', { params });
//     console.log('Get employees response:', response);
//     return response;
//   } catch (error) {
//     console.error('Get employees error:', error);
//     throw error;
//   }
// }

// 员工数据导入导出API
/**
 * 导出员工数据为Excel
 * @param {string} status - 状态参数
 * @returns {Promise} 返回Excel文件的二进制数据
 */
export async function exportEmployees(status) {
  return request.get('/api/employees/export', {
    params: { status },
    responseType: 'blob'
  });
}

/**
 * 导入员工数据
 * @param {File} file - Excel文件
 * @returns {Promise} 返回导入结果
 */
export async function importEmployees(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await request.post('/api/employees/import', formData);
    console.log('Import service response:', response);
    return response;
  } catch (error) {
    console.error('Import service error:', error);
    throw error;
  }
}

/**
 * 获取导入模板
 * @returns {Promise} 返回模板文件的二进制数据
 */
export async function getImportTemplate() {
  try {
    const response = await request.get('/api/employees/import-template', {
      responseType: 'blob',
      headers: {
        'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      }
    });
    return response;
  } catch (error) {
    console.error('获取模板失败:', error);
    throw new Error('获取模板失败');
  }
}

// 教育经历相关API
/**
 * 获取教育经历
 * @param {number} employeeId - 员工ID
 * @returns {Promise} 返回教育经历列表
 */
export async function getEducationHistory(employeeId) {
  return request.get(`/api/employees/${employeeId}/education`);
}

/**
 * 创建教育经历
 * @param {number} employeeId - 员工ID
 * @param {Object} data - 教育经历信息
 * @returns {Promise} 返回创建结果
 */
export async function createEducationHistory(employeeId, data) {
  return request.post(`/api/employees/${employeeId}/education`, data);
}

/**
 * 删除教育经历
 * @param {number} id - 教育经历ID
 * @returns {Promise} 返回删除结果
 */
export async function deleteEducationHistory(id) {
  return request.delete(`/api/employees/education/${id}`);
}

// 工作经历相关API
/**
 * 获取工作经历
 * @param {number} employeeId - 员工ID
 * @returns {Promise} 返回工作经历列表
 */
export async function getWorkHistory(employeeId) {
  return request.get(`/api/employees/${employeeId}/work`);
}

/**
 * 创建工作经历
 * @param {number} employeeId - 员工ID
 * @param {Object} data - 工作经历信息
 * @returns {Promise} 返回创建结果
 */
export async function createWorkHistory(employeeId, data) {
  return request.post(`/api/employees/${employeeId}/work`, data);
}

/**
 * 删除工作经历
 * @param {number} id - 工作经历ID
 * @returns {Promise} 返回删除结果
 */
export async function deleteWorkHistory(id) {
  return request.delete(`/api/employees/work/${id}`);
}

// 调岗历史相关API
/**
 * 获取调岗历史
 * @param {number} employeeId - 员工ID
 * @returns {Promise} 返回调岗历史列表
 */
export async function getPositionChanges(employeeId) {
  return request.get(`/api/employees/${employeeId}/position-changes`);
}

/**
 * 添加调岗记录
 * @param {number} employeeId - 员工ID
 * @param {Object} data - 调岗记录信息
 * @returns {Promise} 返回添加结果
 */
export async function addPositionChange(employeeId, data) {
  return request.post(`/api/employees/${employeeId}/position-changes`, data);
}

/**
 * 更新调岗记录
 * @param {number} employeeId - 员工ID
 * @param {number} changeId - 调岗记录ID
 * @param {Object} data - 更新的调岗记录信息
 * @returns {Promise} 返回更新结果
 */
export async function updatePositionChange(employeeId, changeId, data) {
  return request.put(`/api/employees/${employeeId}/position-changes/${changeId}`, data);
}

/**
 * 删除调岗记录
 * @param {number} employeeId - 员工ID
 * @param {number} changeId - 调岗记录ID
 * @returns {Promise} 返回删除结果
 */
export async function deletePositionChange(employeeId, changeId) {
  return request.delete(`/api/employees/${employeeId}/position-changes/${changeId}`);
}

// 照片和文件上传API
/**
 * 上传员工照片
 * @param {FormData} formData - 包含照片的表单数据
 * @param {number} [employeeId] - 员工ID（可选）
 * @returns {Promise} 返回上传结果
 */
export const uploadPhoto = async (formData, employeeId = null) => {
  try {
    const url = employeeId ? 
      `/api/employees/upload/photo/${employeeId}` : 
      `/api/employees/upload`;
    
    console.log('Uploading photo to:', url);
    console.log('Form data keys:', Array.from(formData.keys()));
    
    // Make sure the file is being sent with the key 'file'
    if (!formData.has('file')) {
      throw new Error('FormData must contain a file with key "file"');
    }
    
    const response = await request.post(url, formData, {
      headers: {
        // Let the browser set the correct Content-Type for FormData
        'Content-Type': 'multipart/form-data',
      },
      withCredentials: true,
    });
    
    console.log('Upload photo response:', response);
    // 直接返回response，因为request.js已经处理了data的提取
    return response;
  } catch (error) {
    console.error('Upload photo error:', error);
    console.error('Error details:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * 上传员工合同
 * @param {FormData} formData - 包含合同文件的表单数据
 * @param {number} employeeId - 员工ID
 * @returns {Promise} 返回上传结果
 */
export const uploadContract = async (formData, employeeId) => {
  try {
    if (!employeeId) {
      throw new Error('未提供员工ID');
    }

    const url = `/api/employees/upload/contract/${employeeId}`;
    console.log('Uploading contract to:', url);
    console.log('Form data keys:', Array.from(formData.keys()));
    
    if (!formData.has('file')) {
      throw new Error('FormData must contain a file with key "file"');
    }
    
    const response = await request.post(url, formData, {
      headers: {
        // Let the browser set the correct Content-Type for FormData
        'Content-Type': 'multipart/form-data',
      },
      withCredentials: true,
    });
    
    console.log('Upload contract response:', response);
    return response;
  } catch (error) {
    console.error('Upload contract error:', error);
    console.error('Error details:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * 获取员工合同列表
 * @param {number} employeeId - 员工ID
 * @returns {Promise} 返回合同列表
 */
export const getEmployeeContracts = async (employeeId) => {
  try {
    const response = await request.get(`/api/employees/${employeeId}/contracts`);
    return response;
  } catch (error) {
    console.error('Get contracts error:', error);
    throw error;
  }
};

/**
 * 预览合同文件
 * @param {string} filename - 文件名
 * @returns {Promise} 返回文件URL
 */
export const previewContract = async (filename) => {
  try {
    const response = await request.get(`/api/employees/contracts/${filename}/preview`, {
      responseType: 'blob'
    });
    return URL.createObjectURL(response);
  } catch (error) {
    console.error('Preview contract error:', error);
    throw error;
  }
};

/**
 * 下载合同文件
 * @param {string} filename - 文件名
 * @returns {Promise} 返回文件Blob
 */
export const downloadContract = async (filename) => {
  try {
    const response = await request.get(`/api/employees/contracts/${filename}/download`, {
      responseType: 'blob'
    });
    const url = URL.createObjectURL(response);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download contract error:', error);
    throw error;
  }
};

// 获取员工统计信息
export async function getEmployeeStats() {
  return request('/api/employee/stats');
}

// 初始化基础数据
/**
 * 初始化基础数据（部门和职位）
 * @returns {Promise} 返回初始化结果
 */
export async function initBaseData() {
  try {
    const [departments, positions] = await Promise.all([
      getDepartments(),
      getPositions()
    ]);
    return {
      departments: departments.data,
      positions: positions.data
    };
  } catch (error) {
    console.error('Init base data error:', error);
    throw error;
  }
}
