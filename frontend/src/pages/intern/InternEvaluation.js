import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Select, DatePicker, message, Space, Rate, Switch, InputNumber, Descriptions, Timeline } from 'antd';
import { getInternStatus, createInternEvaluation, getStatusEvaluations } from '../../services/intern';
import { getPositions } from '../../services/position';
import moment from 'moment';

const { Option } = Select;
const { TextArea } = Input;  

const InternEvaluation = () => {
  const { id } = useParams(); 
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [internStatus, setInternStatus] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [positions, setPositions] = useState([]);

  useEffect(() => {
    fetchInternStatus();
    fetchEvaluations();
    fetchPositions();
  }, [id]);

  const fetchInternStatus = async () => {
    try {
      const res = await getInternStatus(id);
      if (res.code === 200) {
        setInternStatus(res.data);
      }
    } catch (error) {
      message.error('获取实习状态详情失败');
    }
  };

  const fetchEvaluations = async () => {
    try {
      const res = await getStatusEvaluations(id);
      if (res.code === 200) {
        setEvaluations(res.data);
      }
    } catch (error) {
      message.error('获取评估记录失败');
    }
  };

  const fetchPositions = async () => {
    try {
      const res = await getPositions();
      if (res.code === 200) {
        setPositions(res.data);
      }
    } catch (error) {
      message.error('获取职位列表失败');
    }
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      // 从localStorage获取当前用户ID
      const currentUser = JSON.parse(localStorage.getItem('user'));
      const data = {
        ...values,
        intern_status_id: id,
        evaluation_date: values.evaluation_date.format('YYYY-MM-DD'),
        evaluator_id: currentUser.id  // 添加评估人ID
      };
      const res = await createInternEvaluation(data);
      if (res.code === 200) {
        message.success('提交评估成功');
        form.resetFields();
        fetchEvaluations();
      }
    } catch (error) {
      message.error('提交评估失败');
    }
    setLoading(false);
  };

  return (
    <div>
      {/* 实习状态信息 */}
      {internStatus && (
        <Card title="实习信息" style={{ marginBottom: 24 }}>
          <Descriptions>
            <Descriptions.Item label="员工姓名">
              {internStatus.employee_name}
            </Descriptions.Item>
            <Descriptions.Item label="部门">
              {internStatus.department_name}
            </Descriptions.Item>
            <Descriptions.Item label="职位">
              {internStatus.position_name}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              {internStatus.status === 'intern' ? '实习中' :
               internStatus.status === 'probation' ? '试用期' : '正式'}
            </Descriptions.Item>
            <Descriptions.Item label="开始日期">
              {internStatus.start_date}
            </Descriptions.Item>
            <Descriptions.Item label="计划结束日期">
              {internStatus.planned_end_date}
            </Descriptions.Item>
            {internStatus.mentor_name && (
              <Descriptions.Item label="导师">
                {internStatus.mentor_name}
              </Descriptions.Item>
            )}
          </Descriptions>
        </Card>
      )}

      {/* 评估表单 */}
      <Card title="新增评估" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="evaluation_date"
            label="评估日期"
            rules={[{ required: true, message: '请选择评估日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="evaluation_type"
            label="评估类型"
            rules={[{ required: true, message: '请选择评估类型' }]}
          >
            <Select>
              <Option value="monthly">月度评估</Option>
              <Option value="final">转正评估</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="work_performance"
            label="工作表现"
            rules={[{ required: true, message: '请评分工作表现' }]}
          >
            <Rate count={5} />
          </Form.Item>
          <Form.Item
            name="learning_ability"
            label="学习能力"
            rules={[{ required: true, message: '请评分学习能力' }]}
          >
            <Rate count={5} />
          </Form.Item>
          <Form.Item
            name="communication_skill"
            label="沟通能力"
            rules={[{ required: true, message: '请评分沟通能力' }]}
          >
            <Rate count={5} />
          </Form.Item>
          <Form.Item
            name="professional_skill"
            label="专业技能"
            rules={[{ required: true, message: '请评分专业技能' }]}
          >
            <Rate count={5} />
          </Form.Item>
          <Form.Item
            name="attendance"
            label="出勤情况"
            rules={[{ required: true, message: '请评分出勤情况' }]}
          >
            <Rate count={5} />
          </Form.Item>
          <Form.Item
            name="evaluation_content"
            label="评估内容"
            rules={[{ required: true, message: '请填写评估内容' }]}
          >
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item
            name="improvement_suggestions"
            label="改进建议"
          >
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item
            name="is_conversion_evaluation"
            label="是否为转正评估"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => prevValues.is_conversion_evaluation !== currentValues.is_conversion_evaluation}
          >
            {({ getFieldValue }) =>
              getFieldValue('is_conversion_evaluation') ? (
                <>
                  <Form.Item
                    name="conversion_suggestion"
                    label="转正建议"
                    rules={[{ required: true, message: '请填写转正建议' }]}
                  >
                    <TextArea rows={4} maxLength={500} showCount />
                  </Form.Item>

                  <Form.Item
                    name="recommended_position_id"
                    label="建议职位"
                    rules={[{ required: true, message: '请选择建议职位' }]}
                  >
                    <Select>
                      {positions.map(position => (
                        <Option key={position.id} value={position.id}>
                          {position.name}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>

                  <Form.Item
                    name="recommended_salary"
                    label="建议薪资"
                    rules={[{ required: true, message: '请输入建议薪资' }]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      step={1000}
                      formatter={value => `¥ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={value => value.replace(/\¥\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </>
              ) : null
            }
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              提交评估
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* 评估历史 */}
      <Card title="评估历史">
        <Timeline>
          {evaluations.map((evaluation) => (
            <Timeline.Item key={evaluation.id}>
              <h4>{evaluation.evaluation_date} - {evaluation.evaluation_type === 'monthly' ? '月度评估' : '转正评估'}</h4>
              <p>评估人：{evaluation.evaluator_name}</p>
              <p>总分：{evaluation.total_score}</p>
              <p>评估内容：{evaluation.evaluation_content}</p>
              {evaluation.improvement_suggestions && (
                <p>改进建议：{evaluation.improvement_suggestions}</p>
              )}
              {evaluation.conversion_recommended && (
                <>
                  <p>推荐转正：是</p>
                  {evaluation.recommended_position_name && (
                    <p>建议转正职位：{evaluation.recommended_position_name}</p>
                  )}
                  {evaluation.recommended_salary && (
                    <p>建议转正工资：¥{evaluation.recommended_salary}</p>
                  )}
                  {evaluation.conversion_comments && (
                    <p>转正意见：{evaluation.conversion_comments}</p>
                  )}
                </>
              )}
            </Timeline.Item>
          ))}
        </Timeline>
      </Card>
    </div>
  );
};

export default InternEvaluation;
