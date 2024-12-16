import React, { useState, useEffect } from 'react';
import { Table, Button, message } from 'antd';
import { EyeOutlined, DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const ContractList = ({ employeeId }) => {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchContracts = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:5000/api/employees/${employeeId}/contracts`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      if (response.data.code === 200) {
        setContracts(response.data.data);
      }
    } catch (error) {
      message.error('获取合同列表失败');
      console.error('Error fetching contracts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (employeeId) {
      fetchContracts();
    }
  }, [employeeId]);

  const handlePreview = async (record) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/api/employees/preview/contract/${record.id}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
          responseType: 'blob'
        }
      );
      
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      window.URL.revokeObjectURL(url);
    } catch (error) {
      message.error('预览文件失败');
      console.error('Error previewing contract:', error);
    }
  };

  const handleDownload = async (record) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/api/employees/download/contract/${record.id}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
          responseType: 'blob'
        }
      );
      
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = record.file_name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      message.error('下载文件失败');
      console.error('Error downloading contract:', error);
    }
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
    },
    {
      title: '文件类型',
      dataIndex: 'file_type',
      key: 'file_type',
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => moment(text).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Button
            type="link"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record)}
          >
            下载
          </Button>
        </>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={contracts}
      rowKey="id"
      loading={loading}
      pagination={false}
    />
  );
};

export default ContractList;
