import React, { useState } from 'react';
import { Modal, Upload, Button, Space, message } from 'antd';
import { InboxOutlined, DownloadOutlined } from '@ant-design/icons';
import { exportEmployees, importEmployees, getImportTemplate } from '../../../services/employee';

const { Dragger } = Upload;

/**
 * 导入导出模态框组件
 * @param {Object} props - 组件属性
 * @param {boolean} props.visible - 是否显示模态框
 * @param {Function} props.onCancel - 取消回调
 * @param {Function} props.onSuccess - 成功回调
 * @returns {JSX.Element}
 */
const ImportExportModal = ({ visible, onCancel, onSuccess }) => {
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);

  // 处理文件上传
  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', fileList[0]);
    
    setUploading(true);
    
    try {
      const response = await importEmployees(fileList[0]);
      
      message.success(`成功导入 ${response.success_count} 名员工`);
      
      if (response.errors && response.errors.length > 0) {
        Modal.warning({
          title: '部分数据导入失败',
          content: (
            <div>
              {response.errors.map((error, index) => (
                <p key={index}>{error}</p>
              ))}
            </div>
          ),
        });
      }
      
      setFileList([]);
      onSuccess();
    } catch (error) {
      message.error('导入失败');
    } finally {
      setUploading(false);
    }
  };

  // 处理导出
  const handleExport = async () => {
    try {
      const response = await exportEmployees();
      const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `employees_${new Date().getTime()}.xlsx`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      message.error('导出失败');
    }
  };

  // 处理下载模板
  const handleDownloadTemplate = async () => {
    try {
      const response = await getImportTemplate();
      const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'employee_import_template.xlsx';
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      message.error('模板下载失败');
    }
  };

  // 上传组件属性
  const uploadProps = {
    onRemove: () => {
      setFileList([]);
    },
    beforeUpload: (file) => {
      if (!file.name.endsWith('.xlsx')) {
        message.error('只支持.xlsx格式的Excel文件');
        return false;
      }
      setFileList([file]);
      return false;
    },
    fileList,
    maxCount: 1,
  };

  return (
    <Modal
      title="导入导出员工数据"
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={600}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 导出按钮 */}
        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={handleExport}
          block
        >
          导出员工数据
        </Button>

        {/* 下载模板按钮 */}
        <Button
          type="default"
          icon={<DownloadOutlined />}
          onClick={handleDownloadTemplate}
          block
        >
          下载导入模板
        </Button>

        {/* 文件上传区域 */}
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持.xlsx格式的Excel文件，请先下载模板，按照模板格式填写数据后上传
          </p>
        </Dragger>

        {/* 导入按钮 */}
        <Button
          type="primary"
          onClick={handleUpload}
          disabled={fileList.length === 0}
          loading={uploading}
          block
        >
          {uploading ? '导入中...' : '开始导入'}
        </Button>
      </Space>
    </Modal>
  );
};

export default ImportExportModal;
