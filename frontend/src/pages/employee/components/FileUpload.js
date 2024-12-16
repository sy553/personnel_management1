import React, { useState, useEffect } from 'react';
import { Upload, message, Modal } from 'antd';
import { InboxOutlined, PlusOutlined, LoadingOutlined } from '@ant-design/icons';

const { Dragger } = Upload;

const FileUpload = ({ accept, uploadAction, value, imageMode = false, maxSize = 2, defaultIcon, tip, onChange }) => {
  const [loading, setLoading] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewImage, setPreviewImage] = useState('');
  const [fileList, setFileList] = useState([]);

  // 处理图片 URL
  const getImageUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    return `${process.env.REACT_APP_API_BASE_URL}${url}`;
  };

  useEffect(() => {
    if (value) {
      setFileList([
        {
          uid: '-1',
          name: '当前照片',
          status: 'done',
          url: getImageUrl(value)
        }
      ]);
    } else {
      setFileList([]);
    }
  }, [value]);

  const handlePreview = (file) => {
    setPreviewImage(file.url || file.preview);
    setPreviewVisible(true);
  };

  const beforeUpload = (file) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件!');
      return false;
    }
    
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
      message.error('只支持 JPG/PNG/GIF 格式的图片!');
      return false;
    }
    
    const isLt2M = file.size / 1024 / 1024 < maxSize;
    if (!isLt2M) {
      message.error(`图片大小不能超过${maxSize}MB!`);
      return false;
    }
    
    return true;
  };

  const handleUpload = async ({ file, onSuccess: onUploadSuccess, onError }) => {
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await uploadAction(formData);
      
      if (response && response.photo_url) {
        const photoUrl = getImageUrl(response.photo_url);
        const newFile = {
          uid: file.uid,
          name: file.name,
          status: 'done',
          url: photoUrl
        };
        
        setFileList([newFile]);
        
        if (onUploadSuccess) {
          onUploadSuccess(newFile);
        }
        
        if (onChange) {
          onChange(photoUrl);
        }
        
        message.success('照片上传成功！');
      } else {
        throw new Error('未获取到照片URL');
      }
    } catch (error) {
      console.error('上传失败:', error);
      message.error(error.message || '上传失败，请重试');
      if (onError) {
        onError(error);
      }
    } finally {
      setLoading(false);
    }
  };

  const uploadButton = (
    <div>
      {loading ? <LoadingOutlined /> : defaultIcon || <PlusOutlined />}
      <div style={{ marginTop: 8 }}>{tip || '点击上传'}</div>
    </div>
  );

  return (
    <>
      {imageMode ? (
        <Upload
          name="file"
          listType="picture-card"
          showUploadList={false}
          beforeUpload={beforeUpload}
          customRequest={handleUpload}
          onPreview={handlePreview}
        >
          {fileList.length > 0 ? (
            <img
              src={fileList[0].url}
              alt="照片"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          ) : (
            uploadButton
          )}
        </Upload>
      ) : (
        <Dragger {...{
          name: "file",
          multiple: false,
          accept: accept,
          beforeUpload: beforeUpload,
          customRequest: handleUpload,
          showUploadList: false
        }}>
          <p className="ant-upload-drag-icon">
            {defaultIcon || <InboxOutlined />}
          </p>
          <p className="ant-upload-text">{tip || '点击或拖拽文件到此处'}</p>
        </Dragger>
      )}

      <Modal
        open={previewVisible}
        footer={null}
        onCancel={() => setPreviewVisible(false)}
      >
        <img alt="预览" style={{ width: '100%' }} src={previewImage} />
      </Modal>
    </>
  );
};

export default FileUpload;
