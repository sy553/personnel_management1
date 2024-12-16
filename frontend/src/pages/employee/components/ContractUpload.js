import React, { useState, useEffect } from 'react';
import { Upload, message, Button, Space } from 'antd';
import { InboxOutlined, EyeOutlined, DownloadOutlined } from '@ant-design/icons';
import { previewContract, downloadContract } from '../../../services/employee';

const { Dragger } = Upload;

const ContractUpload = ({ uploadAction, value, onChange }) => {
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState([]);

  useEffect(() => {
    if (value) {
      setFileList([
        {
          uid: value.id || '-1',
          name: value.file_name,
          status: 'done',
          url: value.file_url,
          response: value
        }
      ]);
    } else {
      setFileList([]);
    }
  }, [value]);

  const beforeUpload = (file) => {
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const isAllowedType = allowedTypes.includes(file.type);
    if (!isAllowedType) {
      message.error('只支持 PDF/DOC/DOCX 格式的文件!');
      return false;
    }
    
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('文件大小不能超过10MB!');
      return false;
    }
    
    return true;
  };

  const handlePreview = async (file) => {
    try {
      setLoading(true);
      const url = await previewContract(file.response.file_name);
      window.open(url, '_blank');
    } catch (error) {
      console.error('预览失败:', error);
      message.error('预览失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (file) => {
    try {
      setLoading(true);
      await downloadContract(file.response.file_name);
      message.success('下载成功');
    } catch (error) {
      console.error('下载失败:', error);
      message.error('下载失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const customRequest = async ({ file, onSuccess, onError }) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await uploadAction(formData);
      console.log('Upload contract response:', response);
      
      if (response && response.code === 200) {
        const contractData = response.data;
        if (!contractData) {
          throw new Error('未获取到合同信息');
        }
        
        // 创建新的文件对象
        const newFile = {
          uid: contractData.id || file.uid,
          name: contractData.file_name,
          status: 'done',
          url: contractData.file_url,
          response: contractData
        };
        
        // 更新文件列表
        setFileList([newFile]);
        
        // 通知父组件
        if (onChange) {
          onChange(contractData);
        }
        
        message.success('合同上传成功！');
        onSuccess(response, file);
      } else {
        throw new Error(response?.msg || '上传失败');
      }
    } catch (error) {
      console.error('上传失败:', error);
      message.error(error.message || '上传失败，请重试');
      onError(error);
      
      // 清空文件列表
      setFileList([]);
      
      // 通知父组件
      if (onChange) {
        onChange(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const props = {
    name: 'file',
    multiple: false,
    fileList,
    beforeUpload,
    customRequest,
    onRemove: () => {
      setFileList([]);
      if (onChange) {
        onChange(null);
      }
      return true;
    },
    onChange: (info) => {
      // 只在上传开始和删除时更新文件列表
      if (info.file.status === 'uploading' || info.file.status === 'removed') {
        setFileList(info.fileList);
      }
    },
    itemRender: (originNode, file) => {
      // 只有上传成功的文件才显示预览和下载按钮
      if (file.status === 'done' && file.response) {
        return (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            {originNode}
            <Space>
              <Button
                type="link"
                icon={<EyeOutlined />}
                onClick={() => handlePreview(file)}
                loading={loading}
              >
                预览
              </Button>
              <Button
                type="link"
                icon={<DownloadOutlined />}
                onClick={() => handleDownload(file)}
                loading={loading}
              >
                下载
              </Button>
            </Space>
          </div>
        );
      }
      return originNode;
    }
  };

  return (
    <Dragger {...props}>
      <p className="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
      <p className="ant-upload-hint">
        支持 PDF、DOC、DOCX 格式，文件大小不超过10MB
      </p>
    </Dragger>
  );
};

export default ContractUpload;
