import { markRaw } from 'vue';
import type { TemplateItem } from 'ele-admin-plus/es/ele-pro-form-builder/types';
import CoverSingle from './template-covers/cover-single.vue';
import CoverMultiple from './template-covers/cover-multiple.vue';
import CoverGroup from './template-covers/cover-group.vue';
import CoverQuestion from './template-covers/cover-question.vue';
import CoverResume from './template-covers/cover-resume.vue';
import CoverResumeView from './template-covers/cover-resume-view.vue';
import CoverTable from './template-covers/cover-table.vue';
import CoverTableView from './template-covers/cover-table-view.vue';
import CoverTabs from './template-covers/cover-tabs.vue';
import CoverSearch from './template-covers/cover-search.vue';
import CoverDiv from './template-covers/cover-div.vue';

/**
 * 表单模板库数据
 */
export const defaultTemplateData: TemplateItem[] = [
  {
    name: '单列表单',
    cover: markRaw(CoverSingle),
    config: {
      labelWidth: 80,
      footer: true,
      items: [
        {
          key: 'f0sgef2spmqqor03',
          prop: 'reason',
          label: '请假事由',
          type: 'textarea',
          required: true,
          props: {
            placeholder: '请输入请假事由',
            maxlength: 800,
            showWordLimit: true
          }
        },
        {
          key: 'f4acnyndkzqxgduu',
          prop: 'type',
          label: '请假类型',
          type: 'radio',
          required: true,
          props: {
            options: [
              {
                label: '事假',
                value: '1'
              },
              {
                label: '病假',
                value: '2'
              },
              {
                label: '调休',
                value: '3'
              },
              {
                label: '年假',
                value: '4'
              },
              {
                label: '婚嫁',
                value: '5'
              },
              {
                label: '产假',
                value: '6'
              }
            ]
          },
          initValue: '1',
          requiredMessage: '请选择请假类型'
        },
        {
          key: 'f12k0zon5e60rksk',
          prop: 'time',
          label: '起止时间',
          type: 'datetimerange',
          required: true,
          props: {},
          requiredMessage: '请选择起止时间'
        },
        {
          key: 'ferg85hffz2hih8r',
          prop: 'comment',
          label: '备注',
          type: 'textarea',
          required: false,
          props: {
            placeholder: '请输入备注（选填）',
            maxlength: 2000,
            showWordLimit: true
          }
        },
        {
          key: 'fiqzss3ypp57mprj',
          prop: 'attachment',
          label: '图片',
          type: 'imageUpload',
          required: false,
          props: {
            limit: 8
          }
        }
      ]
    }
  },
  {
    name: '多列表单',
    cover: markRaw(CoverMultiple),
    config: {
      labelWidth: 80,
      footer: true,
      items: [
        {
          key: 'fzvl5o0ir7yvbhpb',
          prop: 'reason',
          label: '出差事由',
          type: 'textarea',
          required: true,
          props: {
            placeholder: '请输入出差事由',
            maxlength: 800,
            showWordLimit: true
          }
        },
        {
          key: 'fnsizfrhii2ngvvd',
          prop: 'f316337067sju341',
          label: '',
          type: 'row',
          required: false,
          props: {},
          children: [
            {
              key: 'fc1xz5q53qxbqld4',
              prop: 'f316337067gyx9zh',
              label: '',
              type: 'col',
              props: {
                span: 12,
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'f8ednk4d97mbliqz',
                  prop: 'starting',
                  label: '出发地',
                  type: 'regions',
                  required: true,
                  props: {
                    placeholder: '请选择出发地',
                    type: 'provinceCity',
                    showAllLevels: true
                  }
                }
              ]
            },
            {
              key: 'fd8bjx1kj242lrpf',
              prop: 'f316337067sgbqjm',
              label: '',
              type: 'col',
              props: {
                span: 12,
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'ff8orkcafsw0epc3',
                  prop: 'focus',
                  label: '目的地',
                  type: 'regions',
                  required: true,
                  props: {
                    placeholder: '请选择目的地',
                    type: 'provinceCity',
                    showAllLevels: true
                  }
                }
              ]
            },
            {
              prop: 'f316357134jivuj1',
              label: '',
              type: 'col',
              props: {
                span: 24
              },
              key: 'frccyzgyh7c7eg7k',
              children: [
                {
                  key: 'fz1sea9d5ij2v6fz',
                  prop: 'date',
                  label: '起止日期',
                  type: 'daterange',
                  required: true,
                  props: {},
                  requiredMessage: '请选择起止日期'
                }
              ]
            },
            {
              prop: 'f316439831wzwmai',
              label: '',
              type: 'col',
              props: {
                span: 12,
                xs: {
                  span: 24
                }
              },
              key: 'fdvy5lhhyjyqecev',
              children: [
                {
                  key: 'fc0orbdc1qb9as7y',
                  prop: 'vehicle',
                  label: '交通工具',
                  type: 'radio',
                  required: true,
                  props: {
                    options: [
                      {
                        label: '飞机',
                        value: '1'
                      },
                      {
                        label: '火车',
                        value: '2'
                      },
                      {
                        label: '汽车',
                        value: '3'
                      },
                      {
                        label: '其它',
                        value: '4'
                      }
                    ]
                  },
                  requiredMessage: '请选择交通工具'
                }
              ]
            },
            {
              prop: 'f316441368ez6vei',
              label: '',
              type: 'col',
              props: {
                span: 12,
                xs: {
                  span: 24
                }
              },
              key: 'f9z5f960thgux08d',
              children: [
                {
                  key: 'fg766s0wi7qmihyg',
                  prop: 'type',
                  label: '往返类型',
                  type: 'radio',
                  required: true,
                  props: {
                    options: [
                      {
                        label: '单程',
                        value: '1'
                      },
                      {
                        label: '往返',
                        value: '2'
                      }
                    ]
                  },
                  initValue: '1',
                  requiredMessage: '请选择往返类型'
                }
              ]
            }
          ]
        },
        {
          key: 'f4posldm1936cgpp',
          prop: 'comment',
          label: '备注',
          type: 'textarea',
          required: false,
          props: {
            placeholder: '请输入备注（选填）',
            maxlength: 2000,
            showWordLimit: true
          }
        }
      ]
    }
  },
  {
    name: '分组表单',
    cover: markRaw(CoverGroup),
    config: {
      labelWidth: 94,
      footer: true,
      footerProps: {
        labelWidth: 0
      },
      footerStyle: {
        justifyContent: 'center'
      },
      style: {
        background: 'hsla(216deg, 8%, 50%, 0.08)',
        padding: '16px 16px 1px 16px'
      },
      items: [
        {
          key: 'f8oodwovpso5hdys',
          prop: 'senderInfo',
          type: 'card',
          props: {
            header: '寄件信息',
            bordered: false,
            style: {
              marginBottom: '16px'
            }
          },
          children: [
            {
              key: 'fuuyoc3uxd8nacj6',
              prop: 'fgcdq644x1h53es3',
              label: '',
              type: 'row',
              props: {
                gutter: 20
              },
              children: [
                {
                  key: 'fc18rm3gpphfyig5',
                  prop: 'fa4j3aenmqpoav1e',
                  label: '',
                  type: 'col',
                  props: {
                    span: 12
                  },
                  children: [
                    {
                      key: 'fpl8h24yjnu7dmel',
                      prop: 'senderName',
                      label: '寄件人姓名',
                      type: 'input',
                      required: true,
                      props: {
                        placeholder: '请输入寄件人姓名'
                      }
                    }
                  ]
                },
                {
                  key: 'fayh0sjkcejmb9p5',
                  prop: 'fpknex37szcmc7a9',
                  label: '',
                  type: 'col',
                  props: {
                    span: 12
                  },
                  children: [
                    {
                      key: 'fguc8v7khk1nhcxj',
                      prop: 'senderPhone',
                      label: '寄件人电话',
                      type: 'input',
                      required: true,
                      props: {
                        placeholder: '请输入寄件人电话'
                      }
                    }
                  ]
                },
                {
                  key: 'f7kjmta6d1u6uqoo',
                  prop: 'f52c6iu4dc42xjsr',
                  label: '',
                  type: 'col',
                  props: {
                    span: 24
                  },
                  children: [
                    {
                      key: 'f7myeu6hml2hak64',
                      prop: 'senderAddress',
                      label: '寄件地址',
                      type: 'textarea',
                      required: true,
                      props: {
                        placeholder: '请输入寄件地址'
                      }
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          key: 'f5mamddkbbhubltc',
          prop: 'receiverInfo',
          type: 'card',
          props: {
            header: '收件信息',
            bordered: false,
            style: {
              marginBottom: '16px'
            }
          },
          children: [
            {
              key: 'fjgq9jw3e9iqoqqh',
              prop: 'f6ly2bnrnenpcf4q',
              label: '',
              type: 'row',
              props: {
                gutter: 20
              },
              children: [
                {
                  key: 'fffhyq035sm0y897',
                  prop: 'fhf3r5c89auqkv6x',
                  label: '',
                  type: 'col',
                  props: {
                    span: 12
                  },
                  children: [
                    {
                      key: 'ffr43vz3rtgvzj6x',
                      prop: 'receiverName',
                      label: '收件人姓名',
                      type: 'input',
                      required: true,
                      props: {
                        placeholder: '请输入收件人姓名'
                      }
                    }
                  ]
                },
                {
                  key: 'fbzd2t8doh3gf03l',
                  prop: 'fvdul4lugvawby4h',
                  label: '',
                  type: 'col',
                  props: {
                    span: 12
                  },
                  children: [
                    {
                      key: 'f1v7jk7ilmo3kupl',
                      prop: 'receiverPhone',
                      label: '收件人电话',
                      type: 'input',
                      required: true,
                      props: {
                        placeholder: '请输入收件人电话'
                      }
                    }
                  ]
                },
                {
                  key: 'fvqizaxtvan0kofy',
                  prop: 'f0jupanm70sbc169',
                  label: '',
                  type: 'col',
                  props: {
                    span: 24
                  },
                  children: [
                    {
                      key: 'fz1nt03c3wf8rkbr',
                      prop: 'receiverAddress',
                      label: '收件地址',
                      type: 'textarea',
                      required: true,
                      props: {
                        placeholder: '请输入收件地址'
                      }
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          key: 'f50e9d1j7tf6y9rj',
          prop: 'otherInfo',
          type: 'card',
          props: {
            header: '可折叠卡片',
            bordered: false,
            collapsable: 'header',
            bodyStyle: {
              padding: '0'
            },
            headerStyle: {
              cursor: 'pointer',
              userSelect: 'none'
            },
            style: {
              marginBottom: '16px'
            }
          },
          children: [
            {
              key: 'fc51l0as7k78i2sn',
              prop: 'service',
              label: '快递服务',
              type: 'checkCard',
              props: {
                items: [
                  {
                    label: '顺丰快递',
                    value: '1'
                  },
                  {
                    label: '中通快递',
                    value: '2'
                  },
                  {
                    label: '韵达快递',
                    value: '3'
                  }
                ],
                style: {
                  display: 'flex',
                  alignItems: 'flex-start'
                },
                itemStyle: {
                  padding: '8px 22px',
                  margin: '0 12px 0 0',
                  lineHeight: 'normal'
                }
              },
              required: true,
              itemProps: {
                labelWidth: 80,
                style: {
                  padding: '20px 20px 0 20px'
                }
              },
              requiredMessage: '请选择快递服务'
            },
            {
              key: 'fvk6ye5v7khy7ir5',
              prop: 'privacy',
              label: '隐私保护',
              type: 'checkbox',
              props: {
                options: [
                  {
                    label: '姓名脱敏',
                    value: '1'
                  },
                  {
                    label: '使用虚拟号码',
                    value: '2'
                  },
                  {
                    label: '隐藏地址',
                    value: '3'
                  }
                ]
              },
              itemProps: {
                labelWidth: 80,
                style: {
                  padding: '0 20px 36px 20px',
                  marginBottom: '0'
                }
              }
            }
          ]
        }
      ]
    }
  },
  {
    name: '问卷表单',
    cover: markRaw(CoverQuestion),
    config: {
      labelPosition: 'top',
      labelWidth: 80,
      footer: true,
      footerProps: { labelWidth: 0 },
      footerStyle: { justifyContent: 'center' },
      items: [
        {
          key: 'fy9ixva9wc9cyzx1',
          prop: 'title',
          label: '部门团建活动方案投票',
          type: 'label',
          props: {
            size: 'xl',
            strong: true,
            style: { textAlign: 'center', marginBottom: '18px' }
          }
        },
        {
          key: 'fymxiudq58lask31',
          prop: 'description',
          label:
            '为了感谢各位员工最近对公司发展做出的辛苦付出，也为了增强部门同事之间的凝聚力，开阔员工的视野，让大家在繁忙的工作中放松心情，以更饱满的精神状态迎接新一个月的工作，本部门计划于 06 月 01 日组织团建活动，现在开始征集部门团建活动方案的投票啦~ 请各位同事积极参与，认真填写。',
          type: 'label',
          props: {
            style: {
              textIndent: '2em',
              lineHeight: '28px',
              marginBottom: '28px'
            }
          }
        },
        {
          key: 'fzdjtutjii3k380g',
          prop: 'plan',
          label: '（01）请选择你最喜欢的活动方案(可多选)：',
          required: true,
          requiredMessage: '请选择你最喜欢的活动方案',
          itemProps: { style: { marginBottom: '36px' } },
          type: 'checkbox',
          props: {
            options: [
              { label: '方案一 龙湾度假村一日游', value: '1' },
              { label: '方案二 欢乐谷一日游', value: '2' },
              { label: '方案三 世界城吃饭 + 密室逃脱', value: '3' },
              { label: '方案四 大悦城自助餐 + KTV', value: '4' }
            ],
            style: {
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'stretch',
              paddingLeft: '22px'
            }
          }
        },
        {
          key: 'f2lcxv9k5v9lq9ns',
          prop: 'name',
          label: '（02）您的姓名：',
          required: true,
          requiredMessage: '请输入您的姓名',
          itemProps: { style: { marginBottom: '36px' } },
          type: 'input',
          props: {
            placeholder: '请输入您的姓名',
            style: {
              flex: 1,
              margin: '4px 0 8px 22px',
              maxWidth: '320px'
            }
          }
        },
        {
          key: 'fodwvoktwqe565xn',
          prop: 'family',
          label: '（03）是否携带家属(选是会继续选择携带数量)：',
          required: true,
          requiredMessage: '请选择是否携带家属',
          itemProps: { style: { marginBottom: '36px' } },
          type: 'radio',
          props: {
            options: [
              { label: '是', value: '1' },
              { label: '否', value: '0' }
            ],
            style: {
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'stretch',
              paddingLeft: '22px'
            }
          }
        },
        {
          key: 'f1byxn4hpukjds52',
          prop: 'attendance',
          label: '（04）携带家属数量：',
          required: true,
          requiredMessage: '请选择携带家属数量',
          itemProps: { style: { marginBottom: '36px' } },
          type: 'radio',
          props: {
            options: [
              { label: '携带 1 人', value: '1' },
              { label: '携带 2 人', value: '2' },
              { label: '携带 3 人', value: '3' }
            ],
            style: {
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'stretch',
              paddingLeft: '22px'
            }
          },
          vIf: 'form.family == 1'
        }
      ]
    }
  },
  {
    name: '简历表单',
    cover: markRaw(CoverResume),
    config: {
      labelWidth: 80,
      footer: true,
      footerProps: {
        labelWidth: 0
      },
      footerStyle: {
        justifyContent: 'center'
      },
      items: [
        {
          key: 'f0ulxrplqswvy5ib',
          prop: 'faacqws7lcbhlyom',
          label: '',
          type: 'div',
          props: {
            style: {
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderBottom: '4px solid var(--el-color-primary)',
              margin: '6px 0 38px 0'
            }
          },
          children: [
            {
              key: 'fffaxetsq6rmg3b6',
              prop: 'fpex06b0x4qras8v',
              label: '个人简历',
              type: 'label',
              props: {
                size: 'xl',
                strong: true,
                style: {
                  color: '#fff',
                  background: 'var(--el-color-primary)',
                  padding: '6px 28px 2px 28px',
                  letterSpacing: '6px',
                  borderRadius: '22px 22px 0px 0px'
                }
              }
            }
          ]
        },
        {
          key: 'frsthxd03n6nassq',
          prop: 'fhz9xq8hyc7yxeri',
          label: '',
          type: 'table',
          props: {
            hasHeader: false,
            style: {
              tableLayout: 'fixed',
              border: '0'
            }
          },
          children: [
            {
              key: 'f2fncegapbug2fok',
              prop: 'fts0labgcqju3omx',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'fhd4uw6r0u4du7f4',
                  prop: 'famr4c3y5ebufxi4',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: {
                      border: 'none',
                      background: 'none',
                      borderRadius: '0',
                      padding: '0'
                    }
                  },
                  children: [
                    {
                      key: 'f917fl2oyp0bfxz3',
                      prop: 'f5ng3eco3d2zavpp',
                      label: '',
                      type: 'row',
                      props: {
                        gutter: 16
                      },
                      children: [
                        {
                          key: 'fqinfxb0tku4ehtq',
                          prop: 'fi2dok0vclbz3ve2',
                          label: '',
                          type: 'col',
                          props: {
                            span: 12,
                            xs: {
                              span: 24
                            }
                          },
                          children: [
                            {
                              label: '姓名',
                              prop: 'name',
                              type: 'input',
                              required: true,
                              key: 'fvfbqnj6qifnnz3e',
                              props: {
                                placeholder: '请输入姓名'
                              }
                            }
                          ]
                        },
                        {
                          key: 'f0kxjn4sxev9lbsf',
                          prop: 'fbwmv1xjpcgy5k6i',
                          label: '',
                          type: 'col',
                          props: {
                            span: 12,
                            xs: {
                              span: 24
                            }
                          },
                          children: [
                            {
                              key: 'fz3oksv6kvhc0g0l',
                              prop: 'sex',
                              label: '性别',
                              type: 'radio',
                              props: {
                                options: [
                                  {
                                    label: '男',
                                    value: '男'
                                  },
                                  {
                                    label: '女',
                                    value: '女'
                                  }
                                ]
                              },
                              initValue: '男'
                            }
                          ]
                        },
                        {
                          key: 'f40aykf6p9412frt',
                          prop: 'f02h8957wduyrax1',
                          label: '',
                          type: 'col',
                          props: {
                            span: 12,
                            xs: {
                              span: 24
                            }
                          },
                          children: [
                            {
                              key: 'fm6zzybsancmq55q',
                              prop: 'age',
                              label: '年龄',
                              type: 'inputNumber',
                              required: true,
                              props: {
                                placeholder: '请输入年龄'
                              }
                            }
                          ]
                        },
                        {
                          key: 'fziod8cqcoasrvx5',
                          prop: 'f9lz054eb4ilor78',
                          label: '',
                          type: 'col',
                          props: {
                            span: 12,
                            xs: {
                              span: 24
                            }
                          },
                          children: [
                            {
                              key: 'fwuux2aucs82fpef',
                              prop: 'phone',
                              label: '联系方式',
                              type: 'input',
                              required: true,
                              props: {
                                placeholder: '请输入联系方式'
                              }
                            }
                          ]
                        },
                        {
                          key: 'fc21b2abokf5rfzu',
                          prop: 'fmljqcrqv715j2rj',
                          label: '',
                          type: 'col',
                          props: {
                            span: 12,
                            xs: {
                              span: 24
                            }
                          },
                          children: [
                            {
                              key: 'fbbpgi9m1qqvigsl',
                              prop: 'education',
                              label: '学历',
                              type: 'input',
                              required: true,
                              props: {
                                placeholder: '请输入学历'
                              }
                            }
                          ]
                        },
                        {
                          key: 'fw9lwpw84hdzww5h',
                          prop: 'frajbqsp6v2o298u',
                          label: '',
                          type: 'col',
                          props: {
                            span: 12,
                            xs: {
                              span: 24
                            }
                          },
                          children: [
                            {
                              key: 'fnflzcjq1fgg6nvj',
                              prop: 'experience',
                              label: '工作经验',
                              type: 'input',
                              required: true,
                              props: {
                                placeholder: '请输入工作经验'
                              }
                            }
                          ]
                        },
                        {
                          key: 'fh6gx0f0naf0q9sf',
                          prop: 'fels0t1xalif9vnw',
                          label: '',
                          type: 'col',
                          props: {
                            span: 12,
                            xs: {
                              span: 24
                            }
                          },
                          children: [
                            {
                              key: 'fw6xxmba0tze73hi',
                              prop: 'job',
                              label: '意向岗位',
                              type: 'input',
                              required: true,
                              props: {
                                placeholder: '请输入意向岗位'
                              }
                            }
                          ]
                        },
                        {
                          key: 'f88e8dcfnq9tqocz',
                          prop: 'f56z68ybsw0ts807',
                          label: '',
                          type: 'col',
                          props: {
                            span: 12,
                            xs: {
                              span: 24
                            }
                          },
                          children: [
                            {
                              key: 'f77l5qqags1a7n05',
                              prop: 'salary',
                              label: '期望薪资',
                              type: 'input',
                              required: true,
                              props: {
                                placeholder: '请输入期望薪资'
                              }
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  key: 'frc07z6gnmhcskig',
                  prop: 'fmkl15pfvm5dj172',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: {
                      width: '140px',
                      border: 'none',
                      background: 'none',
                      borderRadius: '0',
                      padding: '0'
                    }
                  },
                  children: [
                    {
                      key: 'fhwkxaon6fqt6owp',
                      prop: 'avatar',
                      label: '头像',
                      type: 'imageUpload',
                      props: {
                        limit: 1,
                        itemStyle: {
                          margin: '0',
                          width: '120px',
                          height: '148px'
                        },
                        buttonStyle: {
                          margin: '0',
                          width: '120px',
                          height: '148px'
                        }
                      },
                      itemProps: {
                        labelWidth: 48,
                        style: {
                          flexDirection: 'column',
                          width: 'max-content',
                          margin: '0 0 0 auto'
                        },
                        labelPosition: 'right'
                      }
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          key: 'ftuhbwjz1zjupc9x',
          label: '',
          prop: 'f7xfvh7gj2z18r2r',
          type: 'div',
          props: {
            style: {
              display: 'flex',
              alignItems: 'center',
              borderBottom: '2px solid var(--el-color-primary)',
              margin: '22px 0 12px 0'
            }
          },
          children: [
            {
              key: 'fb75zjctc226xvnj',
              prop: 'f69o2vkkzykl6iec',
              label: '专业技能',
              type: 'label',
              props: {
                size: 'md',
                strong: true,
                style: {
                  color: '#fff',
                  background: 'var(--el-color-primary)',
                  padding: '4px 20px 2px 20px',
                  letterSpacing: '6px',
                  borderRadius: '12px 12px 0px 0px'
                }
              }
            }
          ]
        },
        {
          key: 'fzsgt968z21chgty',
          prop: 'skill',
          label: '',
          type: 'textarea',
          props: {
            rows: 12,
            placeholder:
              '1、熟练掌握 XXX 语言\n2、熟练使用 XXX 框架\n3、取得 XXX 证书'
          },
          itemProps: {
            labelWidth: 0
          },
          required: true,
          requiredMessage: '请输入专业技能'
        },
        {
          key: 'fq55dqpcem3vjxuj',
          prop: 'f4ku05p3m827gwjm',
          label: '',
          type: 'div',
          props: {
            style: {
              display: 'flex',
              alignItems: 'center',
              borderBottom: '2px solid var(--el-color-primary)',
              margin: '38px 0 20px 0'
            }
          },
          children: [
            {
              key: 'fqxiupsdv93axbq7',
              prop: 'fy20qom1976yb3bl',
              label: '工作经历',
              type: 'label',
              props: {
                size: 'md',
                strong: true,
                style: {
                  color: '#fff',
                  background: 'var(--el-color-primary)',
                  padding: '4px 20px 2px 20px',
                  letterSpacing: '6px',
                  borderRadius: '12px 12px 0px 0px'
                }
              }
            }
          ]
        },
        {
          key: 'frnlpxjyprvpwwck',
          prop: 'fjllat5k38x968x2',
          label: '',
          type: 'row',
          props: {
            gutter: 16
          },
          children: [
            {
              key: 'fhztq1coypiw7azu',
              prop: 'fk89vd6e4su2yu2p',
              label: '',
              type: 'col',
              props: {
                span: 8
              },
              children: [
                {
                  key: 'fwc3u39nypy6fifb',
                  prop: 'careerTime',
                  label: '',
                  type: 'daterange',
                  itemProps: {
                    labelWidth: 0
                  }
                }
              ]
            },
            {
              key: 'f8u4g8prnzcvpoom',
              prop: 'f9en8k4mj2jbpx8j',
              label: '',
              type: 'col',
              props: {
                span: 8
              },
              children: [
                {
                  key: 'fm8ve7akueugbm1g',
                  prop: 'careerCompany',
                  label: '',
                  type: 'input',
                  props: {
                    placeholder: '公司名称'
                  },
                  itemProps: {
                    labelWidth: 0
                  }
                }
              ]
            },
            {
              key: 'f2b9nhjatbg1kbdo',
              prop: 'fi2jydsumdvvl4d6',
              label: '',
              type: 'col',
              props: {
                span: 8
              },
              children: [
                {
                  key: 'f4s1jm9ey3gtiodn',
                  prop: 'careerPost',
                  label: '',
                  type: 'input',
                  props: {
                    placeholder: '岗位名称'
                  },
                  itemProps: {
                    labelWidth: 0
                  }
                }
              ]
            },
            {
              key: 'fnm1y93v26k4hw0r',
              prop: 'fzrnbyn69db1husp',
              label: '',
              type: 'col',
              props: {
                span: 24
              },
              children: [
                {
                  key: 'fu5oqbxkjs6eo2xv',
                  label: '',
                  prop: 'careerJobDescription',
                  type: 'textarea',
                  props: {
                    placeholder:
                      '工作内容：\n负责了什么项目，运用了什么技术，解决了什么难题，取得了什么成果'
                  },
                  itemProps: {
                    labelWidth: 0
                  }
                }
              ]
            }
          ]
        },
        {
          key: 'fa8o77o1uzqnno5s',
          prop: 'fwm8wejh5vuaihep',
          label: '',
          type: 'div',
          props: {
            style: {
              borderTop: '1px dashed var(--el-border-color)',
              paddingTop: '24px',
              marginTop: '12px',
              position: 'relative'
            }
          },
          children: [
            {
              key: 'ftm6u7lh10d4580k',
              prop: 'fwbtw3vttvlva5qr',
              label: '',
              type: 'row',
              props: {
                gutter: 16
              },
              children: [
                {
                  key: 'f5657oh7srzspsrx',
                  prop: 'f2tfk9fa7m3wj3ev',
                  label: '',
                  type: 'col',
                  props: {
                    span: 8
                  },
                  children: [
                    {
                      key: 'fwjks7h51a6v0pe2',
                      label: '',
                      prop: 'career02Time',
                      type: 'daterange',
                      itemProps: {
                        labelWidth: 0
                      }
                    }
                  ]
                },
                {
                  key: 'f6rsshor38kqr42k',
                  prop: 'ffltu7o8fhg6qvpu',
                  label: '',
                  type: 'col',
                  props: {
                    span: 8
                  },
                  children: [
                    {
                      key: 'f893hg5bxkeympla',
                      prop: 'career02Company',
                      label: '',
                      type: 'input',
                      props: {
                        placeholder: '公司名称'
                      },
                      itemProps: {
                        labelWidth: 0
                      }
                    }
                  ]
                },
                {
                  key: 'fsmkxyvpz6y0epnm',
                  prop: 'fbyzt2cxcy2j421i',
                  label: '',
                  type: 'col',
                  props: {
                    span: 8
                  },
                  children: [
                    {
                      key: 'foj1u75f9zkc18dg',
                      prop: 'career02Post',
                      label: '',
                      type: 'input',
                      props: {
                        placeholder: '岗位名称'
                      },
                      itemProps: {
                        labelWidth: 0
                      }
                    }
                  ]
                },
                {
                  key: 'f9qdklxt8f9fulj6',
                  prop: 'fbkew9b5sk0mis49',
                  label: '',
                  type: 'col',
                  props: {
                    span: 24
                  },
                  children: [
                    {
                      key: 'fq0ccecudc9s9e30',
                      prop: 'career02JobDescription',
                      label: '',
                      type: 'textarea',
                      props: {
                        placeholder:
                          '工作内容：\n负责了什么项目，运用了什么技术，解决了什么难题，取得了什么成果'
                      },
                      itemProps: {
                        labelWidth: 0
                      }
                    }
                  ]
                }
              ]
            },
            {
              key: 'fspjph2pv9j8s98g',
              prop: 'showCareer02',
              label: '',
              type: 'checkCard',
              props: {
                items: [
                  {
                    value: '1',
                    label: 'X'
                  }
                ],
                itemStyle: {
                  padding: '3px 0 0 7px',
                  margin: '0',
                  lineHeight: '1',
                  border: 'none',
                  background: '#ff4d4f',
                  color: '#fff',
                  width: '20px',
                  height: '20px',
                  borderRadius: '0px 2px 0px 20px',
                  fontSize: '13px'
                },
                allowUncheck: true,
                arrow: false
              },
              itemProps: {
                labelWidth: 0,
                style: {
                  position: 'absolute',
                  top: '0',
                  right: '0'
                }
              }
            }
          ],
          vIf: '!!form.showCareer02'
        },
        {
          key: 'ft8i0hxrlwv3bfnl',
          prop: 'showCareer03',
          label: '',
          type: 'checkCard',
          props: {
            items: [
              {
                value: '1',
                label: '+ 添加工作经历'
              }
            ],
            style: {
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              marginBottom: '12px'
            },
            itemStyle: {
              padding: '6px 0px',
              margin: '0 0 0 0',
              lineHeight: 'normal',
              textAlign: 'center',
              borderStyle: 'dashed',
              '--ele-check-card-border-color': 'var(--el-border-color)'
            }
          },
          itemProps: {
            labelWidth: 0
          },
          vIf: '!!form.showCareer02&&!form.showCareer03'
        },
        {
          key: 'fhdv5153mpdl2c3u',
          prop: 'f8xxp2ensbjadab9',
          label: '',
          type: 'div',
          props: {
            style: {
              borderTop: '1px dashed var(--el-border-color)',
              paddingTop: '24px',
              marginTop: '12px',
              position: 'relative'
            }
          },
          vIf: '!!form.showCareer03',
          children: [
            {
              key: 'f8hzqinw2dhpt5hl',
              prop: 'f3o80jfuc0knvbey',
              label: '',
              type: 'row',
              props: {
                gutter: 16
              },
              children: [
                {
                  key: 'f1ac57w8rwcexxce',
                  prop: 'fj30sd3vq10s17qk',
                  label: '',
                  type: 'col',
                  props: {
                    span: 8
                  },
                  children: [
                    {
                      key: 'fpolb8pi261ebo90',
                      prop: 'career03Time',
                      label: '',
                      type: 'daterange',
                      itemProps: {
                        labelWidth: 0
                      }
                    }
                  ]
                },
                {
                  key: 'f9ja5vv44h8z4r79',
                  prop: 'f60o8dmhro0d24oq',
                  label: '',
                  type: 'col',
                  props: {
                    span: 8
                  },
                  children: [
                    {
                      key: 'f0bvobgpj9m4mnyd',
                      prop: 'career03Company',
                      label: '',
                      type: 'input',
                      props: {
                        placeholder: '公司名称'
                      },
                      itemProps: {
                        labelWidth: 0
                      }
                    }
                  ]
                },
                {
                  key: 'f7l63ro06p30149r',
                  prop: 'fz0kmdbuyedr9thf',
                  label: '',
                  type: 'col',
                  props: {
                    span: 8
                  },
                  children: [
                    {
                      key: 'fnn0qvr8bgajngux',
                      prop: 'career03Post',
                      label: '',
                      type: 'input',
                      props: {
                        placeholder: '岗位名称'
                      },
                      itemProps: {
                        labelWidth: 0
                      }
                    }
                  ]
                },
                {
                  key: 'frtx8byr0taw5lfp',
                  prop: 'fetpec2npqofwejs',
                  label: '',
                  type: 'col',
                  props: {
                    span: 24
                  },
                  children: [
                    {
                      key: 'fwbvwapfx373ppvx',
                      prop: 'career03JobDescription',
                      label: '',
                      type: 'textarea',
                      props: {
                        placeholder:
                          '工作内容：\n负责了什么项目，运用了什么技术，解决了什么难题，取得了什么成果'
                      },
                      itemProps: {
                        labelWidth: 0
                      }
                    }
                  ]
                }
              ]
            },
            {
              key: 'f990xiiaorw3vv0a',
              prop: 'showCareer03',
              label: '',
              type: 'checkCard',
              props: {
                items: [
                  {
                    value: '1',
                    label: 'X'
                  }
                ],
                itemStyle: {
                  padding: '3px 0 0 7px',
                  margin: '0',
                  lineHeight: '1',
                  border: 'none',
                  background: '#ff4d4f',
                  color: '#fff',
                  width: '20px',
                  height: '20px',
                  borderRadius: '0px 2px 0px 20px',
                  fontSize: '13px'
                },
                allowUncheck: true,
                arrow: false
              },
              itemProps: {
                labelWidth: 0,
                style: {
                  position: 'absolute',
                  top: '0',
                  right: '0'
                }
              }
            }
          ]
        },
        {
          key: 'fwrct8zcshc1wo7t',
          prop: 'showCareer02',
          label: '',
          type: 'checkCard',
          props: {
            items: [
              {
                value: '1',
                label: '+ 添加工作经历'
              }
            ],
            style: {
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              marginBottom: '12px'
            },
            itemStyle: {
              padding: '6px 0px',
              margin: '0 0 0 0',
              lineHeight: 'normal',
              textAlign: 'center',
              borderStyle: 'dashed',
              '--ele-check-card-border-color': 'var(--el-border-color)'
            }
          },
          itemProps: {
            labelWidth: 0
          },
          vIf: '!form.showCareer02'
        },
        {
          key: 'fc6e7h6ye8i0vdrh',
          prop: 'fw87p2968wgs31qb',
          label: '',
          type: 'div',
          props: {
            style: {
              display: 'flex',
              alignItems: 'center',
              borderBottom: '2px solid var(--el-color-primary)',
              margin: '22px 0 20px 0'
            }
          },
          children: [
            {
              prop: 'fqiki56t447la1qt',
              label: '项目经验',
              type: 'label',
              props: {
                size: 'md',
                strong: true,
                style: {
                  color: '#fff',
                  background: 'var(--el-color-primary)',
                  padding: '4px 20px 2px 20px',
                  letterSpacing: '6px',
                  borderRadius: '12px 12px 0px 0px'
                }
              },
              key: 'fppm7wlj12259d4l'
            }
          ]
        },
        {
          key: 'fkqq6zvtf834mnxd',
          prop: 'fgnvnudpzsuwfowb',
          label: '',
          type: 'row',
          props: {
            gutter: 16
          },
          children: [
            {
              key: 'fhxenym961aetikv',
              prop: 'fbnguv0jktlnv9r5',
              label: '',
              type: 'col',
              props: {
                span: 8
              },
              children: [
                {
                  key: 'f39ptfbn1o9vk4no',
                  prop: 'projectTime',
                  label: '',
                  type: 'daterange',
                  itemProps: {
                    labelWidth: 0
                  }
                }
              ]
            },
            {
              key: 'fqf1jyv1r4gton4b',
              prop: 'f8n51wn6v3pudekr',
              label: '',
              type: 'col',
              props: {
                span: 8
              },
              children: [
                {
                  key: 'fqaw36gsnaebdu0i',
                  prop: 'projectName',
                  label: '',
                  type: 'input',
                  props: {
                    placeholder: '项目名称'
                  },
                  itemProps: {
                    labelWidth: 0
                  }
                }
              ]
            },
            {
              key: 'fuqamslrg9t6twxo',
              prop: 'frcpqxyunqsdae9a',
              label: '',
              type: 'col',
              props: {
                span: 8
              },
              children: [
                {
                  key: 'fp0ejckrn4u4xr3t',
                  prop: 'projectRole',
                  label: '',
                  type: 'input',
                  props: {
                    placeholder: 'XX 角色'
                  },
                  itemProps: {
                    labelWidth: 0
                  }
                }
              ]
            },
            {
              key: 'fcr1wx84kaqujc3l',
              prop: 'fvw2ztch7aj9ay52',
              label: '',
              type: 'col',
              props: {
                span: 24
              },
              children: [
                {
                  key: 'fzquft0gv3woh5eg',
                  prop: 'projectDescription',
                  label: '',
                  type: 'textarea',
                  props: {
                    rows: 8,
                    placeholder:
                      '技术栈：框架、数据库、中间件、工具\n团队规模：前端 XX 人、后端 XX 人\n项目简介：\n用于什么行业，包含什么功能，解决什么需求\n工作内容：\n主要负责哪些模块，遇到了什么难题，是如何解决的，从中汲取了什么经验'
                  },
                  itemProps: {
                    labelWidth: 0
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  },
  {
    name: '只读简历表单',
    cover: markRaw(CoverResumeView),
    config: {
      labelWidth: 94,
      footer: false,
      items: [
        {
          key: 'fiv7x3mi1raxsx7o',
          prop: 'fiv7x3mi1raxsx7o',
          label: '',
          type: 'div',
          props: {
            style: {
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderBottom: '4px solid var(--el-color-primary)',
              margin: '6px 0 38px 0'
            }
          },
          children: [
            {
              key: 'f1iz234d9mds0l5j',
              prop: 'f1iz234d9mds0l5j',
              label: '个人简历',
              type: 'label',
              props: {
                size: 'xl',
                strong: true,
                style: {
                  color: '#fff',
                  background: 'var(--el-color-primary)',
                  padding: '6px 28px 2px 28px',
                  letterSpacing: '6px',
                  borderRadius: '22px 22px 0px 0px'
                }
              }
            }
          ]
        },
        {
          key: 'fvtivxypy4n8da1d',
          prop: 'fvtivxypy4n8da1d',
          label: '',
          type: 'table',
          props: {
            hasHeader: false,
            style: { tableLayout: 'fixed', border: '0' }
          },
          children: [
            {
              key: 'fl3jj2fepn8djt17',
              prop: 'fl3jj2fepn8djt17',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'fipngn4mkjgzmwev',
                  prop: 'fipngn4mkjgzmwev',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: {
                      border: 'none',
                      background: 'none',
                      borderRadius: '0',
                      padding: '0'
                    }
                  },
                  children: [
                    {
                      key: 'f8xuc2dg09lycf87',
                      prop: 'f8xuc2dg09lycf87',
                      label: '',
                      type: 'row',
                      props: { gutter: 16 },
                      children: [
                        {
                          key: 'fu72iq8991fikmxp',
                          prop: 'fu72iq8991fikmxp',
                          label: '',
                          type: 'col',
                          props: { span: 12, xs: { span: 24 } },
                          children: [
                            {
                              key: 'fhw598d87a9wln7k',
                              prop: 'name',
                              label: '姓名：',
                              type: 'text',
                              initValue: 'XXX',
                              itemProps: { style: { marginBottom: '0px' } }
                            }
                          ]
                        },
                        {
                          key: 'ff1qhc6vm8zx6wgf',
                          prop: 'ff1qhc6vm8zx6wgf',
                          label: '',
                          type: 'col',
                          props: { span: 12, xs: { span: 24 } },
                          children: [
                            {
                              key: 'ftk5unlssnbnv2oi',
                              prop: 'sex',
                              label: '性别：',
                              type: 'text',
                              initValue: '男',
                              itemProps: { style: { marginBottom: '0px' } }
                            }
                          ]
                        },
                        {
                          key: 'fap2q5ognostoi5b',
                          prop: 'fap2q5ognostoi5b',
                          label: '',
                          type: 'col',
                          props: { span: 12, xs: { span: 24 } },
                          children: [
                            {
                              key: 'fqgk96wtbj5azq4w',
                              prop: 'age',
                              label: '年龄：',
                              type: 'text',
                              initValue: '25',
                              itemProps: { style: { marginBottom: '0px' } }
                            }
                          ]
                        },
                        {
                          key: 'fxwdoyc3rfrqy2p9',
                          prop: 'fxwdoyc3rfrqy2p9',
                          label: '',
                          type: 'col',
                          props: { span: 12, xs: { span: 24 } },
                          children: [
                            {
                              key: 'fqo97mw4gv0qtz8u',
                              label: '联系方式：',
                              prop: 'phone',
                              type: 'text',
                              initValue: '12345678901',
                              itemProps: { style: { marginBottom: '0px' } }
                            }
                          ]
                        },
                        {
                          key: 'f83hu7w7vl0dbfbo',
                          prop: 'f83hu7w7vl0dbfbo',
                          label: '',
                          type: 'col',
                          props: { span: 12, xs: { span: 24 } },
                          children: [
                            {
                              key: 'ffc3k3yrxjskqik8',
                              prop: 'education',
                              label: '学历：',
                              type: 'text',
                              initValue: '本科',
                              itemProps: { style: { marginBottom: '0px' } }
                            }
                          ]
                        },
                        {
                          key: 'f3aumviqxwhqzt7q',
                          prop: 'f3aumviqxwhqzt7q',
                          label: '',
                          type: 'col',
                          props: { span: 12, xs: { span: 24 } },
                          children: [
                            {
                              key: 'fo86pinnd5ubdaqz',
                              prop: 'experience',
                              label: '工作经验：',
                              type: 'text',
                              initValue: '三年',
                              itemProps: { style: { marginBottom: '0px' } }
                            }
                          ]
                        },
                        {
                          key: 'fz2zfsylou3ns3ng',
                          prop: 'fz2zfsylou3ns3ng',
                          label: '',
                          type: 'col',
                          props: { span: 12, xs: { span: 24 } },
                          children: [
                            {
                              key: 'fovn866v7o5ims2e',
                              label: '意向岗位：',
                              prop: 'job',
                              type: 'text',
                              initValue: 'Java 开发工程师',
                              itemProps: { style: { marginBottom: '0px' } }
                            }
                          ]
                        },
                        {
                          key: 'fwyk7mu6605hol7j',
                          prop: 'fwyk7mu6605hol7j',
                          label: '',
                          type: 'col',
                          props: { span: 12, xs: { span: 24 } },
                          children: [
                            {
                              key: 'f2m7rt4qdhp2hevn',
                              prop: 'salary',
                              label: '期望薪资：',
                              type: 'text',
                              initValue: '10K ~ 12K',
                              itemProps: { style: { marginBottom: '0px' } }
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  key: 'fd3f3ei6i15fteg5',
                  prop: 'fd3f3ei6i15fteg5',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: {
                      width: '140px',
                      border: 'none',
                      background: 'none',
                      borderRadius: '0',
                      padding: '0'
                    }
                  },
                  children: [
                    {
                      key: 'fv8s78d5i7e0lb3q',
                      prop: 'avatar',
                      label: '',
                      type: 'imageUpload',
                      props: {
                        limit: 1,
                        itemStyle: {
                          margin: '0',
                          width: '112px',
                          height: '128px',
                          border: 'none',
                          cursor: 'zoom-in'
                        },
                        buttonStyle: {
                          margin: '0',
                          width: '120px',
                          height: '148px'
                        },
                        imageProps: { fit: 'cover' },
                        readonly: true
                      },
                      itemProps: {
                        labelWidth: 0,
                        style: { margin: '0 auto', width: 'max-content' },
                        labelPosition: 'right'
                      },
                      initValue:
                        'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg'
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          key: 'fmzq9sjz6l3l734t',
          prop: 'fmzq9sjz6l3l734t',
          label: '',
          type: 'div',
          props: {
            style: {
              display: 'flex',
              alignItems: 'center',
              borderBottom: '2px solid var(--el-color-primary)',
              margin: '38px 0 16px 0'
            }
          },
          children: [
            {
              key: 'foy1uyb5i7w4rlcn',
              label: '专业技能',
              prop: 'foy1uyb5i7w4rlcn',
              type: 'label',
              props: {
                size: 'md',
                strong: true,
                style: {
                  color: '#fff',
                  background: 'var(--el-color-primary)',
                  padding: '4px 20px 2px 20px',
                  letterSpacing: '6px',
                  borderRadius: '12px 12px 0px 0px'
                }
              }
            }
          ]
        },
        {
          key: 'frnlyc3c8gsi4n5a',
          prop: 'skill',
          label: '',
          type: 'text',
          itemProps: { labelWidth: 0 },
          initValue:
            '1、熟练掌握 Java 基础知识，精通多线程并发，精通 JVM 原理；\n2、熟练使用 MySQL、Redis 及常见的优化手段；\n3、熟练使用 SpringBoot、MyBtais 等主流开发框架；\n4、熟练掌握 RabbitMQ、Kafka、Zookeeper 的使用和原理；\n5、熟练掌握分布式和微服务的系统设计与应用；\n6、熟练掌握常见的 CAP、Paxos 算法；\n7、熟练使用 Git、Maven、Docker 等工具；',
          props: {
            style: { flex: 1, whiteSpace: 'pre-wrap', padding: '0 10px' }
          }
        },
        {
          key: 'fewhnnlxv2j9avp6',
          prop: 'fewhnnlxv2j9avp6',
          label: '',
          type: 'div',
          props: {
            style: {
              display: 'flex',
              alignItems: 'center',
              borderBottom: '2px solid var(--el-color-primary)',
              margin: '38px 0 20px 0'
            }
          },
          children: [
            {
              key: 'fgq1h1s3nqztxjd8',
              prop: 'fgq1h1s3nqztxjd8',
              label: '工作经历',
              type: 'label',
              props: {
                size: 'md',
                strong: true,
                style: {
                  color: '#fff',
                  background: 'var(--el-color-primary)',
                  padding: '4px 20px 2px 20px',
                  letterSpacing: '6px',
                  borderRadius: '12px 12px 0px 0px'
                }
              }
            }
          ]
        },
        {
          key: 'f2yth0acvqt4exug',
          prop: 'fjllat5k38x968x2',
          label: '',
          type: 'row',
          children: [
            {
              key: 'fvc2fa859jgbhgci',
              prop: 'fk89vd6e4su2yu2p',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'fstlpylt11vnr2ou',
                  prop: 'careerTime',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: '2024/02/05 ~ 至今',
                  props: { style: { padding: '0 10px', flex: '1' } }
                }
              ]
            },
            {
              key: 'f6qg7prpeys2pxm9',
              prop: 'f9en8k4mj2jbpx8j',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'fjk5yuj4w8vzx0qs',
                  prop: 'careerCompany',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: 'XXXXX 科技有限公司',
                  props: { style: { flex: '1', textAlign: 'center' } }
                }
              ]
            },
            {
              key: 'fwnvddc2cfhp6gwn',
              prop: 'fi2jydsumdvvl4d6',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'fff22pa8c6zoqqek',
                  prop: 'careerPost',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: 'Java 开发工程师',
                  props: {
                    style: { padding: '0 10px', textAlign: 'right', flex: '1' }
                  }
                }
              ]
            },
            {
              key: 'fnutcb3w031ljfyl',
              prop: 'fzrnbyn69db1husp',
              label: '',
              type: 'col',
              props: { span: 24 },
              children: [
                {
                  key: 'fzfq7sj7iiqutl6h',
                  prop: 'careerJobDescription',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginTop: '6px' } },
                  initValue:
                    '工作内容：\n负责 XXX 业务相关服务的开发和重构以及维护工作，负责线上产品端服务的同步，负责 SSO 单点登录系统后端的架构与开发。',
                  props: {
                    style: {
                      padding: '0 10px',
                      whiteSpace: 'pre-wrap',
                      flex: '1'
                    }
                  }
                }
              ]
            }
          ]
        },
        {
          key: 'fq1l30icpjr7zp52',
          prop: 'fq1l30icpjr7zp52',
          label: '',
          type: 'divider',
          props: { borderStyle: 'dashed', style: { margin: '6px 0 24px 0' } }
        },
        {
          key: 'f3zangv3u57djpu3',
          prop: 'f3zangv3u57djpu3',
          label: '',
          type: 'row',
          children: [
            {
              key: 'f0pm66gzx8gb5u4r',
              prop: 'f0pm66gzx8gb5u4r',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'fn893800624p1s9p',
                  prop: 'career02Time',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: '2023/01/25 ~ 2024/01/02',
                  props: { style: { padding: '0 10px', flex: '1' } }
                }
              ]
            },
            {
              key: 'fl88r5inw6m5sf4z',
              prop: 'fl88r5inw6m5sf4z',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'fs8303qnjos4fwkg',
                  prop: 'career02Company',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: 'XXX 集团股份有限公司',
                  props: { style: { flex: 1, textAlign: 'center' } }
                }
              ]
            },
            {
              key: 'f4gfhepu5faguzt0',
              prop: 'f4gfhepu5faguzt0',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'fmmw6nsmzc7v7di7',
                  prop: 'career02Post',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: 'Java 开发工程师',
                  props: {
                    style: { flex: '1', textAlign: 'right', padding: '0 10px' }
                  }
                }
              ]
            },
            {
              key: 'fi4qrui9wwwjklpp',
              prop: 'fi4qrui9wwwjklpp',
              label: '',
              type: 'col',
              props: { span: 24 },
              children: [
                {
                  key: 'fpntk3iyah2kuyi8',
                  prop: 'career02JobDescription',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginTop: '6px' } },
                  initValue:
                    '工作内容：\n负责了什么项目，运用了什么技术，解决了什么难题，取得了什么成果',
                  props: {
                    style: {
                      flex: '1',
                      whiteSpace: 'pre-wrap',
                      padding: '0 10px'
                    }
                  }
                }
              ]
            }
          ]
        },
        {
          key: 'fj7hl5uhdrliko4j',
          prop: 'fj7hl5uhdrliko4j',
          label: '',
          type: 'div',
          props: {
            style: {
              display: 'flex',
              alignItems: 'center',
              borderBottom: '2px solid var(--el-color-primary)',
              margin: '22px 0 20px 0'
            }
          },
          children: [
            {
              key: 'fjde6xwxl8qrxvqn',
              prop: 'fjde6xwxl8qrxvqn',
              label: '项目经验',
              type: 'label',
              props: {
                size: 'md',
                strong: true,
                style: {
                  color: '#fff',
                  background: 'var(--el-color-primary)',
                  padding: '4px 20px 2px 20px',
                  letterSpacing: '6px',
                  borderRadius: '12px 12px 0px 0px'
                }
              }
            }
          ]
        },
        {
          key: 'fvb8pkk24welfcq4',
          prop: 'fvb8pkk24welfcq4',
          label: '',
          type: 'row',
          children: [
            {
              key: 'f8nda71ma9hvadrh',
              prop: 'f8nda71ma9hvadrh',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'fb4swjzacb9w95aa',
                  prop: 'projectTime',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: '2024/03/22 ~ 2024/06/05',
                  props: { style: { flex: '1', padding: '0 10px' } }
                }
              ]
            },
            {
              key: 'fibucj3vl6ws1z7k',
              prop: 'fibucj3vl6ws1z7k',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'f9k892rcl9muc5r5',
                  prop: 'projectName',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: 'XXX 电商购物平台',
                  props: { style: { flex: '1', textAlign: 'center' } }
                }
              ]
            },
            {
              key: 'f3zjc6w02ovzut23',
              prop: 'f3zjc6w02ovzut23',
              label: '',
              type: 'col',
              props: { span: 8 },
              children: [
                {
                  key: 'fgv29ondn5067cz0',
                  prop: 'projectRole',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginBottom: '0px' } },
                  initValue: '后端开发',
                  props: {
                    style: { flex: '1', textAlign: 'right', padding: '0 10px' }
                  }
                }
              ]
            },
            {
              key: 'fzgngfiaij44ztgd',
              prop: 'fzgngfiaij44ztgd',
              label: '',
              type: 'col',
              props: { span: 24 },
              children: [
                {
                  key: 'f6674rm3v3secpub',
                  prop: 'projectDescription',
                  label: '',
                  type: 'text',
                  itemProps: { labelWidth: 0, style: { marginTop: '12px' } },
                  initValue:
                    '技术栈：SSM、MySQL、Redis、Nginx、MyCat\n团队规模：20人\n项目简介：\n    是一个完整的电商购物平台，主要功能是购物，包含登录、注册、退出登录、购物、支付、退货、换货等模块。\n工作内容：\n    主要负责购物模块，对老旧代码进行重构，解决了访问速度慢的问题，通过 Redis 缓存，解决了高并发问题，将网页的访问速度提高 50%，采用 RabbitMQ 解决不同系统之间的通信问题，并解决了应用 HttpClient 带来的系统耦合问题，使用 Nginx 做反向代理，搭建 Tomcat 服务器集群，实现了系统的高可用、易扩展、高性能。',
                  props: {
                    style: {
                      flex: '1',
                      whiteSpace: 'pre-wrap',
                      padding: '0 10px'
                    }
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  },
  {
    name: '表格表单',
    cover: markRaw(CoverTable),
    config: {
      labelWidth: 80,
      footer: true,
      footerProps: { labelWidth: 0 },
      footerStyle: { justifyContent: 'center' },
      items: [
        {
          key: 'frkqdx8pbeeipguo',
          prop: 'filgf8q0ttascncd',
          label: '员工离职申请表',
          type: 'label',
          props: {
            size: 'xl',
            strong: true,
            style: { textAlign: 'center', marginBottom: '12px' }
          }
        },
        {
          key: 'f645yw5wtzrz4wy8',
          prop: 'f8mvllrtbncy1vsk',
          label: '',
          type: 'table',
          props: {
            border: true,
            hasHeader: false,
            style: {
              '--ele-table-border-color': 'var(--el-text-color-secondary)',
              tableLayout: 'fixed',
              marginBottom: '28px'
            }
          },
          children: [
            {
              key: 'fo7ilm3xia9c9ytg',
              prop: 'f7maev586jyrvvh1',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'fabhugctpvrbkwv3',
                  prop: 'f0f52mfbywogsbti',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: {
                      width: '116px',
                      whiteSpace: 'pre-wrap',
                      textAlign: 'right'
                    }
                  },
                  children: [
                    {
                      key: 'fcz45crf6f4b377u',
                      prop: 'fy41m5s2zkyaefdj',
                      label: '姓        名',
                      type: 'label',
                      props: {
                        tag: 'span',
                        class: 'pro-form-required-asterisk'
                      }
                    }
                  ]
                },
                {
                  key: 'fiqkewjyk9aalxar',
                  prop: 'fhf3dyeerdc48m6m',
                  label: '',
                  type: 'tableCell',
                  props: { style: { minWidth: '140px' } },
                  children: [
                    {
                      key: 'fimctwlzrx8ccyru',
                      prop: 'name',
                      label: '',
                      type: 'input',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' },
                        class: 'pro-form-error-popper'
                      },
                      props: { placeholder: '' },
                      required: true,
                      requiredMessage: '请输入姓名'
                    }
                  ]
                },
                {
                  key: 'f091d418o9fu0ryu',
                  prop: 'f059cggvr7ch4xut',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: {
                      whiteSpace: 'pre-wrap',
                      textAlign: 'right',
                      width: '116px'
                    }
                  },
                  children: [
                    {
                      key: 'f4frr33np66ypdu3',
                      prop: 'f9kasqs7tow2oher',
                      label: '工        号',
                      type: 'label',
                      props: {
                        tag: 'span',
                        class: 'pro-form-required-asterisk'
                      }
                    }
                  ]
                },
                {
                  key: 'fznxki7zikxxg7yj',
                  prop: 'fa0ciq9junkveqnx',
                  label: '',
                  type: 'tableCell',
                  props: { style: { minWidth: '140px' } },
                  children: [
                    {
                      key: 'fq43nwei2zybry6p',
                      prop: 'jobNumber',
                      label: '',
                      type: 'input',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' },
                        class: 'pro-form-error-popper'
                      },
                      props: { placeholder: '' },
                      required: true,
                      requiredMessage: '请输入工号'
                    }
                  ]
                }
              ]
            },
            {
              key: 'f4p3wexw4u83cems',
              prop: 'fk42078emmhdmgqy',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'fqqhrjnh7tdnoir3',
                  prop: 'f2cv4wo8iaf7v3lr',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'right' }
                  },
                  children: [
                    {
                      key: 'f0c5llv1moro606z',
                      prop: 'fxfvpgkr2nc5j5nj',
                      label: '入职日期',
                      type: 'label',
                      props: { tag: 'span' }
                    }
                  ]
                },
                {
                  key: 'f5vu6zevgt4rnbr2',
                  prop: 'fwugrhtwkjgxwktm',
                  label: '',
                  type: 'tableCell',
                  children: [
                    {
                      key: 'f1dz5ppt68m3ezxk',
                      prop: 'commencementDate',
                      label: '',
                      type: 'date',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' },
                        class: 'pro-form-error-popper'
                      },
                      props: { placeholder: '' }
                    }
                  ]
                },
                {
                  key: 'fvag59vog369mlir',
                  prop: 'fjw3r2iyber3jvo7',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'right' }
                  },
                  children: [
                    {
                      key: 'f8mg2zagkx3oke77',
                      prop: 'f8mg2zagkx3oke77',
                      label: '最后工作日',
                      type: 'label',
                      props: { tag: 'span' }
                    }
                  ]
                },
                {
                  key: 'f3zi8dedk39pw2iq',
                  prop: 'fnm7ow3966q7b8ym',
                  label: '',
                  type: 'tableCell',
                  children: [
                    {
                      key: 'fjwifgrvasz0biyu',
                      prop: 'termDate',
                      label: '',
                      type: 'date',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' },
                        class: 'pro-form-error-popper'
                      },
                      props: { placeholder: '' }
                    }
                  ]
                }
              ]
            },
            {
              key: 'fk6dluxgg8v0fcl5',
              prop: 'fcnmncf9ue121uo3',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'fto43t09iuw3dkxx',
                  prop: 'femo1c3f6rreuiai',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'right' }
                  },
                  children: [
                    {
                      key: 'f27xr9mgooi3ngr7',
                      prop: 'fcof4y5h3zxyp33j',
                      label: '所在部门',
                      type: 'label',
                      props: { tag: 'span' }
                    }
                  ]
                },
                {
                  key: 'f6s1ojac3bt2w4rr',
                  prop: 'fvdq5t0dpvxddy6g',
                  label: '',
                  type: 'tableCell',
                  children: [
                    {
                      key: 'f89crqpu73uchyql',
                      prop: 'department',
                      label: '',
                      type: 'input',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      },
                      props: { placeholder: '' }
                    }
                  ]
                },
                {
                  key: 'fk3c6k6rudl0dbry',
                  prop: 'fyjc9vjnbwfo6ka5',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'right' }
                  },
                  children: [
                    {
                      key: 'f7r5o89kl9c97s2i',
                      prop: 'f4v8tsayk8j1neye',
                      label: '岗        位',
                      type: 'label',
                      props: { tag: 'span' }
                    }
                  ]
                },
                {
                  key: 'fvbow7rcae1760ip',
                  prop: 'fzhkjhgrb4x4qze4',
                  label: '',
                  type: 'tableCell',
                  children: [
                    {
                      key: 'fabjg4eu6i2gzgdu',
                      prop: 'post',
                      label: '',
                      type: 'input',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      },
                      props: { placeholder: '' }
                    }
                  ]
                }
              ]
            },
            {
              key: 'f0frak7n6nqknu3r',
              prop: 'fs9mxag9s5ws9zy3',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'fiu572wp9883flfu',
                  prop: 'fxueslwbun47k5dw',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'right' }
                  },
                  children: [
                    {
                      key: 'flc0n9cjkr7qdp3l',
                      prop: 'fpgmne9blazyxia7',
                      label: '离职原因',
                      type: 'label',
                      props: {
                        tag: 'span',
                        class: 'pro-form-required-asterisk'
                      }
                    }
                  ]
                },
                {
                  key: 'f0bcesy1wqohiqkt',
                  prop: 'fxbhulsyjm07fddl',
                  label: '',
                  type: 'tableCell',
                  props: { colspan: '3' },
                  children: [
                    {
                      key: 'fb72stuh2ghyrijv',
                      prop: 'reason',
                      label: '',
                      type: 'textarea',
                      props: { rows: 12, placeholder: '' },
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' },
                        class: 'pro-form-error-popper'
                      },
                      required: true,
                      requiredMessage: '请输入离职原因'
                    },
                    {
                      key: 'fvqkxmt8ja5c9h3n',
                      prop: 'fsm3kxc3fmgya152',
                      label: '申请人签字：_____________    日期：_____________',
                      type: 'label',
                      props: {
                        style: {
                          textAlign: 'right',
                          whiteSpace: 'pre-wrap',
                          margin: '16px 0 10px 0'
                        }
                      }
                    }
                  ]
                }
              ]
            },
            {
              key: 'f5q4jpm3w9drtw5x',
              prop: 'fcsy8oqcn2kmkrcr',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'f8qmfyd96eeh5z6w',
                  prop: 'feu23hb6wpgcsuxi',
                  label: '',
                  type: 'tableCell',
                  props: { colspan: '4' },
                  children: [
                    {
                      key: 'fle76eb5pdo1tmyk',
                      prop: 'fs5voxssme7se0xh',
                      label: '部门意见：',
                      type: 'label',
                      props: { style: { marginBottom: '12px' } }
                    },
                    {
                      key: 'fjj1qx1zfcs0ztfq',
                      prop: 'opinion',
                      label: '',
                      type: 'textarea',
                      props: { placeholder: '' },
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      }
                    },
                    {
                      key: 'fbn8ffyor0vzdidw',
                      prop: 'f2pg82osz3sb7snv',
                      label:
                        '部门主管签字：_____________    日期：_____________',
                      type: 'label',
                      props: {
                        style: {
                          textAlign: 'right',
                          whiteSpace: 'pre-wrap',
                          margin: '16px 0 10px 0'
                        }
                      }
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  },
  {
    name: '只读表格表单',
    cover: markRaw(CoverTableView),
    config: {
      labelWidth: 80,
      footer: false,
      items: [
        {
          key: 'fula2npbkf819vh4',
          prop: 'fula2npbkf819vh4',
          label: '员工离职申请表',
          type: 'label',
          props: {
            size: 'xl',
            strong: true,
            style: { textAlign: 'center', marginBottom: '12px' }
          }
        },
        {
          key: 'fh4u0cks93v4xxrb',
          prop: 'fh4u0cks93v4xxrb',
          label: '',
          type: 'table',
          props: {
            border: true,
            hasHeader: false,
            style: {
              '--ele-table-border-color': 'var(--el-text-color-secondary)',
              '--ele-table-tr-hover-bg': 'transparent',
              '--ele-table-radius': 0,
              tableLayout: 'fixed'
            }
          },
          children: [
            {
              key: 'f1p7dng7gz69jnnc',
              prop: 'f1p7dng7gz69jnnc',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'fj2phamyozphw4xi',
                  prop: 'fj2phamyozphw4xi',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: {
                      width: '100px',
                      whiteSpace: 'pre-wrap',
                      textAlign: 'center'
                    }
                  },
                  children: [
                    {
                      key: 'fxonm77f6yq9pekm',
                      prop: 'fxonm77f6yq9pekm',
                      label: '姓        名',
                      type: 'label'
                    }
                  ]
                },
                {
                  key: 'fujcysrf7u85czpb',
                  prop: 'fujcysrf7u85czpb',
                  label: '',
                  type: 'tableCell',
                  props: { style: { minWidth: '140px' } },
                  children: [
                    {
                      key: 'fmb3pjtfgzt9qizp',
                      prop: 'name',
                      label: '',
                      type: 'text',
                      initValue: 'XXX',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      }
                    }
                  ]
                },
                {
                  key: 'fgou2bsavvrbk2ak',
                  prop: 'fgou2bsavvrbk2ak',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: {
                      width: '100px',
                      whiteSpace: 'pre-wrap',
                      textAlign: 'center'
                    }
                  },
                  children: [
                    {
                      key: 'fixj69j8xc42xl37',
                      prop: 'fixj69j8xc42xl37',
                      label: '性        别',
                      type: 'label'
                    }
                  ]
                },
                {
                  key: 'fsqsvduns5ao7qno',
                  prop: 'fsqsvduns5ao7qno',
                  label: '',
                  type: 'tableCell',
                  props: { style: { minWidth: '140px' } },
                  children: [
                    {
                      key: 'fji3s1oks50mp66b',
                      prop: 'sex',
                      label: '',
                      type: 'text',
                      initValue: '男',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      }
                    }
                  ]
                }
              ]
            },
            {
              key: 'fv4etxh10otlj3qx',
              prop: 'fv4etxh10otlj3qx',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'ft8rejnjn1isf7h3',
                  prop: 'ft8rejnjn1isf7h3',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'center' }
                  },
                  children: [
                    {
                      key: 'fgh1spj9nnqjkjn9',
                      prop: 'fgh1spj9nnqjkjn9',
                      label: '工        号',
                      type: 'label'
                    }
                  ]
                },
                {
                  key: 'fx78mg3zbijrmc8c',
                  prop: 'fx78mg3zbijrmc8c',
                  label: '',
                  type: 'tableCell',
                  children: [
                    {
                      key: 'fmmwlj9t047uyv8m',
                      prop: 'jobNumber',
                      label: '',
                      type: 'text',
                      initValue: '026',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      }
                    }
                  ]
                },
                {
                  key: 'fx63wiqttcy6nlnv',
                  prop: 'fx63wiqttcy6nlnv',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'center' }
                  },
                  children: [
                    {
                      key: 'fur99irp6wcxkqv3',
                      prop: 'fur99irp6wcxkqv3',
                      label: '入职日期',
                      type: 'label'
                    }
                  ]
                },
                {
                  key: 'fefn3xk6rosdr13r',
                  prop: 'fefn3xk6rosdr13r',
                  label: '',
                  type: 'tableCell',
                  children: [
                    {
                      key: 'fgzpkfe32e6rpp7c',
                      prop: 'commencementDate',
                      label: '',
                      type: 'text',
                      initValue: '2021/11/04',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      },
                      props: { style: { wordBreak: 'break-all' } }
                    }
                  ]
                }
              ]
            },
            {
              key: 'ffpqy7162hcuahon',
              prop: 'ffpqy7162hcuahon',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'flqdmju7mhfgv9fm',
                  prop: 'flqdmju7mhfgv9fm',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'center' }
                  },
                  children: [
                    {
                      key: 'fbujfamh5vmmu8fu',
                      prop: 'fbujfamh5vmmu8fu',
                      label: '所在部门',
                      type: 'label'
                    }
                  ]
                },
                {
                  key: 'fvsp66elfr0q4eth',
                  prop: 'fvsp66elfr0q4eth',
                  label: '',
                  type: 'tableCell',
                  children: [
                    {
                      key: 'ffbrwwjekvr2j8dk',
                      prop: 'department',
                      label: '',
                      type: 'text',
                      initValue: '研发部',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      }
                    }
                  ]
                },
                {
                  key: 'fxnluohhd036e6om',
                  prop: 'fxnluohhd036e6om',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'center' }
                  },
                  children: [
                    {
                      key: 'fjhm798qeofzd0dm',
                      prop: 'fjhm798qeofzd0dm',
                      label: '岗        位',
                      type: 'label'
                    }
                  ]
                },
                {
                  key: 'frn1bqlkol2ekp22',
                  prop: 'frn1bqlkol2ekp22',
                  label: '',
                  type: 'tableCell',
                  children: [
                    {
                      key: 'fb8dc1fxedvd1wos',
                      prop: 'post',
                      label: '',
                      type: 'text',
                      initValue: 'Java 开发工程师',
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      }
                    }
                  ]
                }
              ]
            },
            {
              key: 'fgsq9m2yh2fg6iqc',
              prop: 'fgsq9m2yh2fg6iqc',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'f3okqh9zfgjbmh76',
                  prop: 'f3okqh9zfgjbmh76',
                  label: '',
                  type: 'tableCell',
                  props: {
                    style: { whiteSpace: 'pre-wrap', textAlign: 'center' }
                  },
                  children: [
                    {
                      key: 'f5s46dbjq4rbf25d',
                      prop: 'f5s46dbjq4rbf25d',
                      label: '离职原因',
                      type: 'label'
                    }
                  ]
                },
                {
                  key: 'flhqteuml38v4jnw',
                  prop: 'flhqteuml38v4jnw',
                  label: '',
                  type: 'tableCell',
                  props: { colspan: '3' },
                  children: [
                    {
                      key: 'fis63jfwjs4ji9ft',
                      prop: 'reason',
                      label: '',
                      type: 'text',
                      initValue:
                        '我非常感谢在这里的工作经历，但我一直寻求在技术上和职业生涯上有更大的突破，在过去的一段时间里，我努力工作并为公司做出了不少贡献，然而，我注意到我的薪资水平并没有得到相应的提升，最近我收到了一份薪资更高、更具挑战性的工作邀请，它更符合我的职业发展规划，因此我决定接受这个机会，离开现在的环境！',
                      props: {
                        style: { textIndent: '2em', minHeight: '260px' }
                      },
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      }
                    },
                    {
                      key: 'fgejhff67u1xobsm',
                      prop: 'fgejhff67u1xobsm',
                      label: '申请人签字：_____________    日期：_____________',
                      type: 'label',
                      props: {
                        style: {
                          textAlign: 'right',
                          whiteSpace: 'pre-wrap',
                          marginBottom: '10px'
                        }
                      }
                    }
                  ]
                }
              ]
            },
            {
              key: 'fcc82kwpd2rrmdx0',
              prop: 'fcc82kwpd2rrmdx0',
              label: '',
              type: 'tableRow',
              children: [
                {
                  key: 'f31bua69jjaeu7si',
                  prop: 'f31bua69jjaeu7si',
                  label: '',
                  type: 'tableCell',
                  props: { colspan: '4' },
                  children: [
                    {
                      key: 'farwg0pvzu2a391k',
                      prop: 'farwg0pvzu2a391k',
                      label: '部门意见：',
                      type: 'label',
                      props: { style: { marginBottom: '12px' } }
                    },
                    {
                      key: 'fjd5sgqz0y8wa839',
                      prop: 'opinion',
                      label: '',
                      type: 'text',
                      initValue: '所有工作内容都已经交接完毕，同意离职！',
                      props: { style: { minHeight: '120px' } },
                      itemProps: {
                        labelWidth: 0,
                        style: { marginBottom: '0px' }
                      }
                    },
                    {
                      key: 'fxiele7md6dampim',
                      prop: 'fxiele7md6dampim',
                      label:
                        '部门主管签字：_____________    日期：_____________',
                      type: 'label',
                      props: {
                        style: {
                          textAlign: 'right',
                          whiteSpace: 'pre-wrap',
                          marginBottom: '10px'
                        }
                      }
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  },
  {
    name: '选项卡表单',
    cover: markRaw(CoverTabs),
    config: {
      labelWidth: 94,
      footer: true,
      footerProps: {
        labelWidth: 0
      },
      footerStyle: {
        justifyContent: 'center'
      },
      items: [
        {
          key: 'fibmpsyy92r2zday',
          prop: 'titleText1',
          label: '卡片风格的选项卡',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '0 0 16px 0'
            }
          }
        },
        {
          key: 'fgmklrcqwx5vqzmr',
          prop: 'tab1',
          label: '',
          type: 'tabs',
          children: [
            {
              key: 'fcnyklgwl68qo76f',
              prop: 'senderInfo',
              type: 'tabPane',
              props: {
                label: '寄件信息'
              },
              children: [
                {
                  key: 'fbs1rmmy8629o7vt',
                  prop: 'fno4ts7elzjf7ita',
                  label: '',
                  type: 'row',
                  props: {
                    gutter: 20
                  },
                  children: [
                    {
                      key: 'fcdcgw9sowjprh3x',
                      prop: 'fd7ytymasw31p707',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'fkxkeaizbzgbfmsc',
                          label: '寄件人姓名',
                          prop: 'senderName',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入寄件人姓名'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fmubw6fnj7g4kfgg',
                      prop: 'f64c34oq0qmwgb5r',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'fv41tn45llj8nbxn',
                          label: '寄件人电话',
                          prop: 'senderPhone',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入寄件人电话'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fx6w9gvo54ivhxa5',
                      prop: 'fm52k73gjl5uc6we',
                      label: '',
                      type: 'col',
                      props: {
                        span: 24
                      },
                      children: [
                        {
                          key: 'fjwd5gej1evu0m8m',
                          label: '寄件地址',
                          prop: 'senderAddress',
                          type: 'textarea',
                          required: true,
                          props: {
                            placeholder: '请输入寄件地址'
                          }
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              key: 'f0kkofxrqsb5w2fw',
              prop: 'receiverInfo',
              type: 'tabPane',
              props: {
                label: '收件信息'
              },
              children: [
                {
                  key: 'f6b062nbp3ynnlyo',
                  prop: 'f57262iw1oac2a77',
                  label: '',
                  type: 'row',
                  props: {
                    gutter: 20
                  },
                  children: [
                    {
                      key: 'fix0iq1h01ernjdv',
                      prop: 'fssdc1216v5zhhga',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'fgqrz2sjsu61rtwq',
                          label: '收件人姓名',
                          prop: 'receiverName',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入收件人姓名'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fy4jpy3jn13imk0g',
                      prop: 'fugygwvfvekc7lu5',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'ff2iy6qmr4b9zq9t',
                          label: '收件人电话',
                          prop: 'receiverPhone',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入收件人电话'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fj5w7up9gmikyr14',
                      prop: 'f4bc9n71gaap7kg0',
                      label: '',
                      type: 'col',
                      props: {
                        span: 24
                      },
                      children: [
                        {
                          key: 'fdhnusoztrq1a4li',
                          prop: 'receiverAddress',
                          label: '收件地址',
                          type: 'textarea',
                          required: true,
                          props: {
                            placeholder: '请输入收件地址'
                          }
                        },
                        {
                          key: 'fdsx9diwfzeo2u9p',
                          prop: 'privacy',
                          label: '隐私保护',
                          type: 'checkbox',
                          props: {
                            options: [
                              {
                                label: '姓名脱敏',
                                value: '1'
                              },
                              {
                                label: '使用虚拟号码',
                                value: '2'
                              },
                              {
                                label: '隐藏地址',
                                value: '3'
                              }
                            ]
                          }
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          key: 'fpk0y5p3ghy4iydi',
          prop: 'titleText2',
          label: '默认风格的选项卡',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '32px 0 16px 0'
            }
          }
        },
        {
          key: 'fvdd6x15inmuq2x0',
          prop: 'tab2',
          label: '',
          type: 'tabs',
          props: {
            type: 'default'
          },
          children: [
            {
              key: 'fy7inn0wj7ulf2fk',
              prop: 'tab2_senderInfo',
              type: 'tabPane',
              props: {
                label: '寄件信息'
              },
              children: [
                {
                  key: 'f5o08z4thuwvr5v7',
                  prop: 'fh5buocjxrilg7re',
                  label: '',
                  type: 'row',
                  props: {
                    gutter: 20
                  },
                  children: [
                    {
                      key: 'fuvhb55f4pv3yvhg',
                      prop: 'fuuixzhf146vbmeo',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          label: '寄件人姓名',
                          prop: 'senderName2',
                          type: 'input',
                          required: true,
                          key: 'fgde9fpsix3e5f5u',
                          itemProps: {
                            style: {
                              marginTop: '20px'
                            }
                          },
                          props: {
                            placeholder: '请输入寄件人姓名'
                          }
                        }
                      ]
                    },
                    {
                      key: 'ff3ptathjmbe2xs6',
                      prop: 'f0mot6jwdlgz60t6',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'f69i8zpjr6pmg6c0',
                          label: '寄件人电话',
                          prop: 'senderPhone2',
                          type: 'input',
                          required: true,
                          itemProps: {
                            style: {
                              marginTop: '20px'
                            }
                          },
                          props: {
                            placeholder: '请输入寄件人电话'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fsv9hhlk5ebqvc56',
                      prop: 'f8bvnaej2ft23g65',
                      label: '',
                      type: 'col',
                      props: {
                        span: 24
                      },
                      children: [
                        {
                          key: 'fubs5u3fpf4jh90n',
                          label: '寄件地址',
                          prop: 'senderAddress2',
                          type: 'textarea',
                          required: true,
                          props: {
                            placeholder: '请输入寄件地址'
                          }
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              key: 'fgz0np8sexvbpmq7',
              prop: 'tab2_receiverInfo',
              type: 'tabPane',
              props: {
                label: '收件信息'
              },
              children: [
                {
                  key: 'f18yxduo76cgirhh',
                  prop: 'f0jyy4jx3xgwlwpk',
                  label: '',
                  type: 'row',
                  props: {
                    gutter: 20
                  },
                  children: [
                    {
                      key: 'fenc5jvxts5h64v5',
                      prop: 'f1ju0dgdhhvl4l2b',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'fhawf0gffmv633vt',
                          prop: 'receiverName2',
                          label: '收件人姓名',
                          type: 'input',
                          required: true,
                          itemProps: {
                            style: {
                              marginTop: '20px'
                            }
                          },
                          props: {
                            placeholder: '请输入收件人姓名'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fvysy40r76lak5bb',
                      prop: 'fpfkh2ucy5ru7ycz',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'fusim02hxcuddm8g',
                          prop: 'receiverPhone2',
                          label: '收件人电话',
                          type: 'input',
                          required: true,
                          itemProps: {
                            style: {
                              marginTop: '20px'
                            }
                          },
                          props: {
                            placeholder: '请输入收件人电话'
                          }
                        }
                      ]
                    },
                    {
                      prop: 'famlbj0a85oxndz6',
                      label: '',
                      type: 'col',
                      props: {
                        span: 24
                      },
                      key: 'fshsssaynmabvn5z',
                      children: [
                        {
                          key: 'flvo5q4bgf6vr0v7',
                          prop: 'receiverAddress2',
                          label: '收件地址',
                          type: 'textarea',
                          required: true,
                          props: {
                            placeholder: '请输入收件地址'
                          }
                        },
                        {
                          key: 'f9eswwsr562fjze6',
                          prop: 'privacy2',
                          label: '隐私保护',
                          type: 'checkbox',
                          props: {
                            options: [
                              {
                                label: '姓名脱敏',
                                value: '1'
                              },
                              {
                                label: '使用虚拟号码',
                                value: '2'
                              },
                              {
                                label: '隐藏地址',
                                value: '3'
                              }
                            ]
                          }
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          key: 'f1py73zs4vxdpfkg',
          prop: 'tab2',
          label: '',
          type: 'checkCard',
          props: {
            items: [
              {
                label: '切换到“收件信息”',
                value: 'tab2_receiverInfo'
              }
            ],
            style: {
              display: 'flex',
              alignItems: 'flex-start'
            },
            itemStyle: {
              color: '#fff',
              margin: '0 12px 0 0',
              padding: '0 12px',
              background: 'var(--el-color-primary)',
              border: 'none'
            }
          },
          vIf: "!form.tab2 || form.tab2 == 'tab2_senderInfo'",
          itemProps: {
            labelWidth: 0
          }
        },
        {
          key: 'f0qmevsnifd5un2s',
          prop: 'tab2',
          label: '',
          type: 'checkCard',
          props: {
            items: [
              {
                label: '切换到“寄件信息”',
                value: 'tab2_senderInfo'
              }
            ],
            style: {
              display: 'flex',
              alignItems: 'flex-start'
            },
            itemStyle: {
              color: '#fff',
              margin: '0 12px 0 0',
              padding: '0 12px',
              background: 'var(--el-color-primary)',
              border: 'none'
            }
          },
          vIf: "form.tab2 == 'tab2_receiverInfo'",
          itemProps: {
            labelWidth: 0
          }
        }
      ]
    }
  },
  {
    name: '搜索表单',
    cover: markRaw(CoverSearch),
    config: {
      labelWidth: 80,
      grid: {
        md: 8,
        sm: 12,
        xs: 24
      },
      footer: true,
      footerProps: {
        labelWidth: 16
      },
      autoFooterCol: true,
      showSearchExpand: true,
      submitText: '搜索',
      items: [
        {
          label: '用户账号',
          prop: 'username',
          type: 'input',
          key: 'fu39ruuab4dfamxa',
          props: {
            placeholder: '请输入'
          }
        },
        {
          label: '用户名',
          prop: 'nickname',
          type: 'input',
          key: 'fz1dzyiymoq8fdaf',
          props: {
            placeholder: '请输入用户名'
          }
        },
        {
          label: '性别',
          prop: 'sex',
          type: 'dictSelect',
          props: {
            code: 'sex',
            placeholder: '请选择性别'
          },
          vIf: 'searchExpand',
          key: 'fkhgycwgm8fk7ov0'
        },
        {
          label: '角色',
          prop: 'roles',
          type: 'multipleSelect',
          props: {
            options: [
              {
                label: '管理员',
                value: 1
              },
              {
                label: '普通用户',
                value: 2
              },
              {
                label: '游客',
                value: 3
              }
            ],
            placeholder: '请选择角色'
          },
          vIf: 'searchExpand',
          key: 'fmz5rjc53cy38eqd'
        },
        {
          label: '邮箱',
          prop: 'email',
          type: 'input',
          vIf: 'searchExpand',
          key: 'fc4a4teb9k8nqudr',
          props: {
            placeholder: '请输入邮箱'
          }
        },
        {
          label: '手机号',
          prop: 'phone',
          type: 'input',
          vIf: 'searchExpand',
          key: 'f2btybgpeees1z92',
          props: {
            placeholder: '请输入手机号'
          }
        },
        {
          label: '出生日期',
          prop: 'birthday',
          type: 'date',
          vIf: 'searchExpand',
          key: 'fb3ppq6nd9yz5bb1',
          props: {
            placeholder: '请选择出生日期'
          }
        }
      ]
    }
  },
  {
    name: '更多高级示例',
    cover: markRaw(CoverDiv),
    config: {
      labelWidth: 94,
      footer: true,
      footerProps: {
        labelWidth: 0
      },
      footerStyle: {
        justifyContent: 'center'
      },
      items: [
        {
          key: 'f06ezklpxbyyaj2b',
          label: '自定义搜索表单布局',
          prop: 'fzn3b56g88kfnnhn',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '6px 0 22px 0'
            }
          }
        },
        {
          key: 'fghotn8wcnau3wtz',
          prop: 'fmikzii9bgqoqpjr',
          label: '',
          type: 'row',
          required: false,
          props: {
            gutter: 0
          },
          children: [
            {
              prop: 'fzi1bfqvwziegu44',
              type: 'col',
              key: 'fwottkv7rvpnj6mi',
              props: {
                span: null,
                md: {
                  span: 8
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'f6rc8le3kwfcdln0',
                  prop: 'f83x34ospvbvm16g',
                  label: '用户账号',
                  type: 'input',
                  required: false,
                  props: {
                    placeholder: '请输入用户账号'
                  },
                  itemProps: {
                    labelWidth: 80
                  }
                }
              ]
            },
            {
              prop: 'fkln4gksqzq8nz0y',
              type: 'col',
              key: 'f0x5zax4bq5q3rvz',
              props: {
                span: null,
                md: {
                  span: 8
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'fek80ak0dxyas6q1',
                  prop: 'fw828cyeb0yqq4jv',
                  label: '用户名',
                  type: 'input',
                  required: false,
                  props: {
                    placeholder: '请输入用户名'
                  },
                  itemProps: {
                    labelWidth: 80
                  }
                }
              ]
            },
            {
              prop: 'foh3l6i36qemv2jv',
              type: 'col',
              key: 'fbybr9m9iy9vmy4b',
              props: {
                span: null,
                md: {
                  span: 8
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'fpwapl2syfv2vlsv',
                  prop: 'fc1bqbd4pyxjjbw9',
                  label: '性别',
                  type: 'select',
                  required: false,
                  props: {
                    placeholder: '请选择性别',
                    options: [
                      {
                        label: '男',
                        value: '男'
                      },
                      {
                        label: '女',
                        value: '女'
                      }
                    ]
                  },
                  itemProps: {
                    labelWidth: 80
                  }
                }
              ],
              vIf: 'form.fsubrbvz39c3eiqv === true'
            },
            {
              prop: 'fdx2n4qnttz4is67',
              type: 'col',
              key: 'f3sa30b1uniie45o',
              props: {
                span: null,
                md: {
                  span: 8
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'f29vj6w62ozh9hy4',
                  prop: 'fkmmkt4s6n8p2xeq',
                  label: '角色',
                  type: 'select',
                  required: false,
                  props: {
                    placeholder: '请选择角色',
                    options: [
                      {
                        label: '男',
                        value: '男'
                      },
                      {
                        label: '女',
                        value: '女'
                      }
                    ]
                  },
                  itemProps: {
                    labelWidth: 80
                  }
                }
              ],
              vIf: 'form.fsubrbvz39c3eiqv === true'
            },
            {
              prop: 'fyghhip4y3ic6tuc',
              type: 'col',
              key: 'fi4plmts2ikwfo8a',
              props: {
                span: null,
                md: {
                  span: 8
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'f031c4zk2bxu0kpx',
                  prop: 'f9ad1qgpphh9br3b',
                  label: '邮箱',
                  type: 'input',
                  required: false,
                  props: {
                    placeholder: '请输入邮箱'
                  },
                  itemProps: {
                    labelWidth: 80
                  }
                }
              ],
              vIf: 'form.fsubrbvz39c3eiqv === true'
            },
            {
              prop: 'fxbq9y220fv6pwyi',
              type: 'col',
              key: 'fsx2dgwfov2mvvwe',
              props: {
                span: null,
                md: {
                  span: 8
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'fr6almf4v71nipsb',
                  prop: 'fy778appcwq1u7aq',
                  label: '手机号',
                  type: 'input',
                  required: false,
                  props: {
                    placeholder: '请输入手机号'
                  },
                  itemProps: {
                    labelWidth: 80
                  }
                }
              ],
              vIf: 'form.fsubrbvz39c3eiqv === true'
            },
            {
              prop: 'foxr3jrpc2vg2bhs',
              type: 'col',
              key: 'ffrzv01lquyxfc8r',
              props: {
                span: null,
                md: {
                  span: 8
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'fd2bf12k608dodsg',
                  prop: 'frg673r5objxo8kb',
                  label: '出生日期',
                  type: 'date',
                  required: false,
                  props: {
                    placeholder: '请选择出生日期'
                  },
                  itemProps: {
                    labelWidth: 80
                  }
                }
              ],
              vIf: 'form.fsubrbvz39c3eiqv === true'
            },
            {
              prop: 'fj50a7p0drngaidf',
              type: 'col',
              key: 'fv48fuc0d63gnm0u',
              props: {
                span: null,
                md: {
                  span: 16
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'fa3xh2rf06ehh286',
                  prop: 'fn30zzt112btg45t',
                  label: '',
                  type: 'div',
                  required: false,
                  props: {
                    style: {
                      display: 'flex',
                      alignItems: 'center',
                      paddingLeft: '16px',
                      justifyContent: 'flex-end'
                    }
                  },
                  containerDraggable: false,
                  children: [
                    {
                      key: 'f7gxm86agd8335yz',
                      prop: 'fgbbk345g2xe08uz',
                      label: '',
                      type: 'div',
                      required: false,
                      props: {},
                      containerDraggable: true,
                      children: [
                        {
                          key: 'fd3fvqeuo1sohezv',
                          prop: 'f1dhule4vpeqt6yh',
                          label: '搜索',
                          type: 'button',
                          required: false,
                          props: {}
                        }
                      ]
                    },
                    {
                      key: 'fxfstlqk9ewhxnwu',
                      prop: 'f8kfrjrii402ml9o',
                      label: '',
                      type: 'div',
                      required: false,
                      props: {
                        style: {
                          paddingLeft: '12px'
                        }
                      },
                      containerDraggable: true,
                      children: [
                        {
                          key: 'fyyqilvv88iih91i',
                          prop: 'ftvpox3mv42ey5ta',
                          label: '重置',
                          type: 'button',
                          required: false,
                          props: {
                            size: 'default',
                            type: 'default',
                            plain: false
                          },
                          itemProps: {
                            labelWidth: 94,
                            labelPosition: 'right'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fds2bsbvz0dt6h8b',
                      prop: 'fh9m4l23jlmxaty8',
                      label: '',
                      type: 'div',
                      required: false,
                      props: {},
                      containerDraggable: true,
                      children: [
                        {
                          key: 'foay2krkkbqs4j95',
                          prop: 'fsubrbvz39c3eiqv',
                          label: ' 收起',
                          type: 'label',
                          required: false,
                          props: {
                            icon: 'IconProArrowUp',
                            type: 'primary',
                            style: {
                              cursor: 'pointer',
                              marginLeft: '12px'
                            },
                            onClick:
                              '/*__PRO_FORM__*/(enent) => {\n    form.fsubrbvz39c3eiqv = !form.fsubrbvz39c3eiqv;\n}'
                          }
                        }
                      ]
                    }
                  ]
                }
              ],
              vIf: 'form.fsubrbvz39c3eiqv === true'
            },
            {
              prop: 'f3ucfmrp886v4wpq',
              type: 'col',
              key: 'fw1q9b6259aw7xrh',
              props: {
                span: null,
                md: {
                  span: 8
                },
                sm: {
                  span: 12
                },
                xs: {
                  span: 24
                }
              },
              children: [
                {
                  key: 'fbdhme6gxlnhe0il',
                  prop: 'fkhyfi8c4pyowstd',
                  label: '',
                  type: 'div',
                  required: false,
                  props: {
                    style: {
                      display: 'flex',
                      alignItems: 'center',
                      paddingLeft: '16px'
                    }
                  },
                  containerDraggable: false,
                  children: [
                    {
                      key: 'fv1krz16v8y5udx4',
                      prop: 'fbl8xs4rw5l0qwe2',
                      label: '',
                      type: 'div',
                      required: false,
                      props: {},
                      containerDraggable: true,
                      children: [
                        {
                          key: 'fw57sa4vienggjoy',
                          prop: 'fa41x4uj2m7vvivk',
                          label: '搜索',
                          type: 'button',
                          required: false,
                          props: {}
                        }
                      ]
                    },
                    {
                      key: 'f68bwb7jynefmont',
                      prop: 'fwi63umnd8f8zgkj',
                      label: '',
                      type: 'div',
                      required: false,
                      props: {
                        style: {
                          paddingLeft: '12px'
                        }
                      },
                      containerDraggable: true,
                      children: [
                        {
                          key: 'f2j4spmxgep4m3q4',
                          prop: 'fma4czk8f5kcnrrk',
                          label: '重置',
                          type: 'button',
                          required: false,
                          props: {
                            size: 'default',
                            type: 'default',
                            plain: false
                          },
                          itemProps: {
                            labelWidth: 94,
                            labelPosition: 'right'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fejlx7v18uh7ny2l',
                      prop: 'f8rcllwcyul5xnzl',
                      label: '',
                      type: 'div',
                      required: false,
                      props: {},
                      containerDraggable: true,
                      children: [
                        {
                          key: 'fozelvgdqq6indne',
                          prop: 'f22kpsz9kxh94kn0',
                          label: ' 展开',
                          type: 'label',
                          required: false,
                          props: {
                            icon: 'IconProArrowDown',
                            type: 'primary',
                            style: {
                              cursor: 'pointer',
                              marginLeft: '12px'
                            },
                            onClick:
                              '/*__PRO_FORM__*/(enent) => {\n    form.fsubrbvz39c3eiqv = !form.fsubrbvz39c3eiqv;\n}'
                          }
                        }
                      ]
                    }
                  ]
                }
              ],
              vIf: '!form.fsubrbvz39c3eiqv'
            }
          ]
        },
        {
          key: 'f5v32qim01tixh3o',
          label: '使用折叠面板组件',
          prop: 'filuy7tx6vlbdoe1',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '42px 0 22px 0'
            }
          }
        },
        {
          key: 'f7ma9aizwf8is86z',
          prop: 'collapse1',
          label: '',
          type: 'collapse',
          props: {
            accordion: true,
            style: {
              marginBottom: '20px'
            }
          },
          children: [
            {
              key: 'fh4sz7bjbswgx971',
              prop: 'senderInfo',
              type: 'collapseItem',
              props: {
                title: '寄件信息'
              },
              children: [
                {
                  key: 'fnzl2593yt8dgzsp',
                  prop: 'ftpmou8tncyfp5v6',
                  label: '',
                  type: 'row',
                  required: false,
                  props: {
                    gutter: 20
                  },
                  children: [
                    {
                      prop: 'ft84hgakobr12jwd',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      key: 'f3tn225gtbfv9dc4',
                      children: [
                        {
                          key: 'ftqxca8gl5syz93z',
                          prop: 'senderName',
                          label: '寄件人姓名',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入寄件人姓名'
                          }
                        }
                      ]
                    },
                    {
                      key: 'f3w35epnzdokzu0d',
                      prop: 'foxoymo8un5iwi88',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'fly3m5pf3zlo0ila',
                          prop: 'senderPhone',
                          label: '寄件人电话',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入寄件人电话'
                          }
                        }
                      ]
                    },
                    {
                      key: 'ftbrfyjf14ced62y',
                      prop: 'fdhdl830pdfegmzj',
                      label: '',
                      type: 'col',
                      props: {
                        span: 24
                      },
                      children: [
                        {
                          key: 'f2mqqdm5fqgoy7ci',
                          prop: 'senderAddress',
                          label: '寄件地址',
                          type: 'textarea',
                          required: true,
                          props: {
                            placeholder: '请输入寄件地址'
                          }
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              key: 'f5zsvt1h635r837f',
              prop: 'receiverInfo',
              type: 'collapseItem',
              props: {
                title: '收件信息'
              },
              children: [
                {
                  key: 'fe5zh8awlnvurd17',
                  prop: 'f40lp463cchlv6gk',
                  label: '',
                  type: 'row',
                  required: false,
                  props: {
                    gutter: 20
                  },
                  children: [
                    {
                      key: 'fokfuqowmzmi1m9c',
                      prop: 'fmh264yd5aahiv46',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'fgdqe47hd46oykeq',
                          prop: 'receiverName',
                          label: '收件人姓名',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入收件人姓名'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fl49e57okcg5any3',
                      prop: 'fdgkscnuxkc5yj74',
                      label: '',
                      type: 'col',
                      props: {
                        span: 12,
                        xs: {
                          span: 24
                        }
                      },
                      children: [
                        {
                          key: 'fck3glap332gow16',
                          prop: 'receiverPhone',
                          label: '收件人电话',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入收件人电话'
                          }
                        }
                      ]
                    },
                    {
                      key: 'fvvl1x39yb23nn1n',
                      prop: 'flfepq5dd9ik4zii',
                      label: '',
                      type: 'col',
                      props: {
                        span: 24
                      },
                      children: [
                        {
                          key: 'fjdfhqsqwnaacmh3',
                          prop: 'receiverAddress',
                          label: '收件地址',
                          type: 'textarea',
                          required: true,
                          props: {
                            placeholder: '请输入收件地址'
                          }
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          key: 'fjcbu2832y4ntsr3',
          prop: 'collapse1',
          label: '',
          type: 'checkCard',
          props: {
            items: [
              {
                label: '展开“收件信息”',
                value: 'receiverInfo'
              }
            ],
            style: {
              display: 'flex',
              alignItems: 'flex-start'
            },
            itemStyle: {
              color: '#fff',
              margin: '0 12px 0 0',
              padding: '0 12px',
              background: 'var(--el-color-primary)',
              border: 'none'
            }
          },
          vIf: "!form.collapse1 || form.collapse1 == 'senderInfo'",
          itemProps: {
            labelWidth: 0
          }
        },
        {
          key: 'fyl51um35bi2tg6s',
          prop: 'collapse1',
          label: '',
          type: 'checkCard',
          props: {
            items: [
              {
                label: '展开“寄件信息”',
                value: 'senderInfo'
              }
            ],
            style: {
              display: 'flex',
              alignItems: 'flex-start'
            },
            itemStyle: {
              color: '#fff',
              margin: '0 12px 0 0',
              padding: '0 12px',
              background: 'var(--el-color-primary)',
              border: 'none'
            }
          },
          vIf: "form.collapse1 == 'receiverInfo'",
          itemProps: {
            labelWidth: 0
          }
        },
        {
          key: 'f8hba9ohldpupdjd',
          label: '使用轮播图组件',
          prop: 'f9d0a57nvyuuhyl7',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '42px 0 22px 0'
            }
          }
        },
        {
          key: 'f51ic86s27rsfiel',
          prop: 'fazoiq7tevtgxtn3',
          label: '',
          type: 'carousel',
          props: {
            type: 'card'
          },
          children: [
            {
              key: 'ffcjob63ymssp8g0',
              prop: 'f8qygq27s55tuvao',
              label: '',
              type: 'carouselItem',
              props: {
                style: {
                  background:
                    'top left/100% url(https://cdn.eleadmin.com/20200610/yeKvhT20lMU0f1T3Y743UlGEOLLnZSnp.jpg)'
                }
              },
              children: [
                {
                  key: 'fpplsd3pg6w0xd9u',
                  prop: 'fjd1zcr9quvuxfne',
                  label: '',
                  type: 'div',
                  props: {
                    style: {
                      height: '100%'
                    }
                  },
                  children: [
                    {
                      key: 'fqr15rkuw4vif4bm',
                      prop: 'fcnpq5b1zjxh83kd',
                      label: '',
                      type: 'div',
                      props: {
                        is: 'img',
                        src: 'https://cdn.eleadmin.com/20200610/yeKvhT20lMU0f1T3Y743UlGEOLLnZSnp.jpg',
                        style: {
                          width: 'auto',
                          height: '100%',
                          objectFit: 'contain',
                          display: 'block',
                          margin: '0 auto',
                          maskImage:
                            'linear-gradient(to right, transparent 4%, rgba(0, 0, 0, 1) 12%, rgba(0, 0, 0, 1) 88%, transparent 96%)'
                        }
                      }
                    }
                  ]
                }
              ]
            },
            {
              key: 'f80fmii1xlh52e11',
              prop: 'fqc3jpweagfxxzue',
              label: '',
              type: 'carouselItem',
              props: {
                style: {
                  background:
                    'bottom left/76% url(https://cdn.eleadmin.com/20200610/4Z0QR2L0J1XStxBh99jVJ8qLfsGsOgjU.jpg)'
                }
              },
              children: [
                {
                  key: 'fw80nod7bci64rra',
                  prop: 'fglszgd2wd322bcb',
                  label: '',
                  type: 'div',
                  props: {
                    style: {
                      backdropFilter: 'blur(2px)',
                      height: '100%'
                    }
                  },
                  children: [
                    {
                      key: 'fjsa0vdg801364ki',
                      prop: 'frt34s0efcpyn1xd',
                      label: '',
                      type: 'div',
                      props: {
                        is: 'img',
                        src: 'https://cdn.eleadmin.com/20200610/4Z0QR2L0J1XStxBh99jVJ8qLfsGsOgjU.jpg',
                        style: {
                          width: 'auto',
                          height: '100%',
                          objectFit: 'contain',
                          display: 'block',
                          margin: '0 auto',
                          maskImage:
                            'linear-gradient(to right, transparent 4%, rgba(0, 0, 0, 1) 12%, rgba(0, 0, 0, 1) 88%, transparent 96%)'
                        }
                      }
                    }
                  ]
                }
              ]
            },
            {
              key: 'fnhvuq5udvxf0xdj',
              prop: 'ffz14kse8h6zyfuz',
              label: '',
              type: 'carouselItem',
              props: {
                style: {
                  background:
                    'left bottom/100% url(https://cdn.eleadmin.com/20200610/fAenQ8nvRjL7x0i0jEfuDBZHvJfHf3v6.jpg)'
                }
              },
              children: [
                {
                  key: 'frvgn26ug8kj5tol',
                  prop: 'fuyg7z9mua4746gm',
                  label: '',
                  type: 'div',
                  props: {
                    style: {
                      backdropFilter: 'blur(2px)',
                      height: '100%'
                    }
                  },
                  children: [
                    {
                      key: 'f50bj207zbs60cdw',
                      prop: 'furrw3les1jp48q8',
                      label: '',
                      type: 'div',
                      props: {
                        is: 'img',
                        src: 'https://cdn.eleadmin.com/20200610/fAenQ8nvRjL7x0i0jEfuDBZHvJfHf3v6.jpg',
                        style: {
                          width: 'auto',
                          height: '100%',
                          objectFit: 'contain',
                          display: 'block',
                          margin: '0 auto',
                          maskImage:
                            'linear-gradient(to right, transparent 4%, rgba(0, 0, 0, 1) 12%, rgba(0, 0, 0, 1) 88%, transparent 96%)'
                        }
                      }
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          key: 'fbtm4gewx2xlzecm',
          prop: 'f0nhvyfv5qolw0mz',
          label: '使用布局组件',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '42px 0 22px 0'
            }
          }
        },
        {
          key: 'f9z3edvdc84qp2nm',
          prop: 'framHeader1',
          label: '',
          type: 'div',
          props: {
            style: {
              background: '#3C3C3C',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              height: '24px',
              borderTopLeftRadius: '6px',
              borderTopRightRadius: '6px',
              padding: '0 12px'
            }
          },
          children: [
            {
              key: 'fu6qg1viq9sbsup2',
              prop: 'fram1Icon1',
              label: '',
              type: 'div',
              props: {
                style: {
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: '#ff4a4a'
                }
              }
            },
            {
              key: 'fg3fbnssu501g2cr',
              prop: 'fram1Icon2',
              label: '',
              type: 'div',
              props: {
                style: {
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: '#ffb83d'
                }
              }
            },
            {
              key: 'fb4d5oxnb1upilrk',
              prop: 'fram1Icon3',
              label: '',
              type: 'div',
              props: {
                style: {
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: '#00c543'
                }
              }
            }
          ]
        },
        {
          key: 'fc5k5bq0gjdt8cf1',
          prop: 'framBody1',
          label: '',
          type: 'div',
          props: {
            style: {
              border: '7px solid #3C3C3C',
              borderBottomLeftRadius: '6px',
              borderBottomRightRadius: '6px',
              borderTop: 'none',
              overflow: 'hidden',
              position: 'relative',
              zIndex: 99
            }
          },
          children: [
            {
              key: 'f5fa9bw9bgvd7ecz',
              prop: 'layout1',
              label: '',
              type: 'adminLayout',
              props: {
                height: '520px',
                fixedBody: true,
                logoSrc: 'https://cdn.eleadmin.com/20200610/logo.svg',
                logoTitle: 'ProForm',
                logoInHeader: true,
                headerCustomStyle: {
                  gap: '22px'
                },
                menuScrollToActive: false,
                layout: 'mix',
                sidebarLayout: 'box',
                sideboxActive: '/user',
                sideboxMenus: [
                  {
                    index: '/user',
                    title: '用户管理',
                    icon: 'IconProUserOutlined'
                  },
                  {
                    index: '/order',
                    title: '订单管理',
                    icon: 'IconProUserOutlined'
                  }
                ],
                headerMenus: [
                  {
                    index: '/personnel',
                    title: '人事系统',
                    icon: 'IconProUserOutlined'
                  },
                  {
                    index: '/finance',
                    title: '财务系统',
                    icon: 'IconProUserOutlined'
                  }
                ],
                headerActive: '/personnel',
                compact: false,
                collapse: false,
                tabBar: false,
                breadcrumb: false,
                backTop: false,
                sidebarStyle: 'light'
              },
              children: [
                {
                  key: 'fb8hkn6iprg6tms0',
                  prop: 'userInfoWrap',
                  label: '',
                  type: 'div',
                  props: {
                    style: {
                      padding: '16px'
                    }
                  },
                  children: [
                    {
                      key: 'fyyznwe3exe3zyk4',
                      prop: 'userInfoCard',
                      type: 'card',
                      props: {
                        header: '新增用户',
                        bordered: false
                      },
                      children: [
                        {
                          key: 'fo2w3f38h63dace3',
                          label: '用户名',
                          prop: 'username',
                          type: 'input',
                          required: true,
                          props: {
                            placeholder: '请输入用户名'
                          }
                        },
                        {
                          key: 'fzogtgydtp9lpqci',
                          label: '性别',
                          prop: 'sex',
                          type: 'radio',
                          props: {
                            options: [
                              {
                                label: '男',
                                value: '1'
                              },
                              {
                                label: '女',
                                value: '2'
                              }
                            ]
                          },
                          required: true,
                          requiredMessage: '请选择性别'
                        },
                        {
                          key: 'fo1tjsri6dlpf9sv',
                          prop: 'role',
                          label: '角色',
                          type: 'multipleCheckCard',
                          props: {
                            items: [
                              {
                                label: '管理员',
                                value: '1'
                              },
                              {
                                label: '普通用户',
                                value: '2'
                              }
                            ],
                            style: {
                              display: 'flex',
                              alignItems: 'flex-start'
                            },
                            itemStyle: {
                              padding: '8px 22px',
                              margin: '0 12px 0 0',
                              lineHeight: 'normal'
                            }
                          },
                          required: true,
                          requiredMessage: '请选择角色'
                        }
                      ]
                    }
                  ],
                  containerDraggable: true
                }
              ]
            }
          ],
          containerDraggable: true
        },
        {
          key: 'fww4qt5kbkeb87cj',
          prop: 'fxuszraejibtmexg',
          label: '使用图标',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '42px 0 22px 0'
            }
          }
        },
        {
          key: 'fs3to8l8mn8m6ozn',
          prop: 'textPrimary1',
          label: ' 主色文本',
          type: 'label',
          props: {
            type: 'primary',
            icon: 'IconProUserOutlined'
          }
        },
        {
          key: 'fbgfph9avdj67lp9',
          prop: 'textSuccess1',
          label: ' 成功文本',
          type: 'label',
          props: {
            type: 'success',
            icon: 'IconProCheckCircleOutlined',
            style: {
              marginTop: '12px'
            }
          }
        },
        {
          key: 'fe1f3zgo79xknj4e',
          prop: 'textDefault1',
          label: '后置图标',
          type: 'label',
          props: {
            style: {
              marginTop: '12px'
            }
          },
          children: [
            {
              key: 'fh4xbjrobvsay7qz',
              prop: 'fpkm2d6mmrpsib2h',
              type: 'icon',
              props: {
                name: 'IconProCheckCircleOutlined',
                style: {
                  marginLeft: '4px',
                  verticalAlign: '-2px'
                }
              }
            }
          ]
        },
        {
          key: 'f24p2978ldecrqxp',
          prop: 'btnIconWrap',
          label: '',
          type: 'div',
          props: {
            style: {
              margin: '22px 0 0 0'
            }
          },
          children: [
            {
              key: 'fgatxyehnnoro2ak',
              prop: 'btnIcon1',
              label: '前置图标',
              type: 'button',
              props: {
                icon: 'IconProUserOutlined',
                class: 'ele-btn-icon'
              }
            },
            {
              key: 'fffawohn4fh1vmpk',
              prop: 'btnIcon2',
              label: '后置图标',
              type: 'button',
              props: {
                class: 'ele-btn-icon'
              },
              children: [
                {
                  key: 'fuu07ztffpmjhf51',
                  prop: 'f6cew8ltcgdvpge2',
                  type: 'icon',
                  required: false,
                  props: {
                    name: 'IconProCheckCircleOutlined',
                    style: {
                      marginLeft: '4px'
                    }
                  }
                }
              ]
            }
          ],
          containerDraggable: true
        },
        {
          key: 'fu0zvawyxz2eq1u4',
          prop: 'ffmyjz9r7e6hagp7',
          label: '按钮事件处理',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '42px 0 22px 0'
            }
          }
        },
        {
          key: 'fts2o7sksxmgouxs',
          prop: 'demoSteps',
          label: '',
          type: 'steps',
          props: {
            items: [
              {
                title: '第一步',
                description: '填写转账信息'
              },
              {
                title: '第二步',
                description: '确认转账信息'
              },
              {
                title: '第三步',
                description: '转账成功'
              }
            ],
            finishStatus: 'success'
          }
        },
        {
          key: 'f3y98sj9kyw2bock',
          prop: 'btnStepsWrap',
          label: '',
          type: 'div',
          props: {
            style: {
              margin: '16px 0 0 0'
            }
          },
          children: [
            {
              key: 'fujcd5gu4dy97yog',
              prop: 'btnPrevSteps',
              label: '上一步',
              type: 'button',
              props: {
                type: 'default',
                onClick:
                  '/*__PRO_FORM__*/() => {\r\n    if (form.demoSteps > 0) {\r\n        form.demoSteps--;\r\n    }\r\n}'
              }
            },
            {
              key: 'faw5yvvtayu7gzx6',
              prop: 'btnNextSteps',
              label: '下一步',
              type: 'button',
              props: {
                onClick:
                  '/*__PRO_FORM__*/() => {\r\n    if (!form.demoSteps) {\r\n        form.demoSteps = 1;\r\n    } else if (form.demoSteps < 3) {\r\n        form.demoSteps++;\r\n    }\r\n}'
              }
            }
          ],
          containerDraggable: true
        },
        {
          key: 'fmwzd2hgas3mmx94',
          prop: 'ftzavv3otsce65ob',
          label: '使用远程数据',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '42px 0 22px 0'
            }
          }
        },
        {
          key: 'fg1wqocio0k8z6mg',
          prop: 'f7hct9l9edwsfgco',
          label: '',
          type: 'div',
          required: false,
          props: {
            style: {
              display: 'flex'
            }
          },
          children: [
            {
              key: 'fzo9zeo7w0jc3yt2',
              prop: 'f2z8obfekhla82xp',
              label: '',
              type: 'div',
              required: false,
              props: {
                style: {
                  width: '320px',
                  maxWidth: '100%'
                }
              },
              children: [
                {
                  key: 'fg6uszfd7xtkurqu',
                  prop: 'ft5a9dzi73asjpmg',
                  label: '用户名',
                  type: 'input',
                  required: false,
                  props: {
                    placeholder: ''
                  },
                  itemProps: {
                    labelWidth: 66,
                    style: {
                      marginBottom: '0'
                    }
                  }
                }
              ],
              containerDraggable: true
            },
            {
              key: 'fawbevmhzacfukqo',
              prop: 'foh3c22ecuh1cawh',
              label: '',
              type: 'div',
              required: false,
              props: {
                style: {
                  flex: '1',
                  paddingLeft: '16px'
                }
              },
              children: [
                {
                  key: 'f712nyz43xwl6q5p',
                  prop: 'fy7ezfq0dnwx82cl',
                  label: '搜索',
                  type: 'button',
                  required: false,
                  props: {
                    onClick:
                      "/*__PRO_FORM__*/(enent) => {\n    getProFormRefs()['fawnh9xd81lytli3Ref']?.reload?.({ page: 1 });\n}"
                  }
                }
              ],
              containerDraggable: true
            }
          ],
          containerDraggable: false
        },
        {
          key: 'ffsu1a81hk95ynfq',
          prop: 'fawnh9xd81lytli3',
          label: '',
          type: 'proTable',
          required: false,
          props: {
            showOverflowTooltip: true,
            datasource:
              "/*__PRO_FORM__*/async ({ pages, orders }) => {\n    const res = await httpRequest.get('/system/user/page', {\n        params: Object.assign({}, pages, orders, {\n            nickname: form.ft5a9dzi73asjpmg\n        })\n    });\n    return res.data.data;\n}",
            columns: [
              {
                type: 'index',
                columnKey: 'index',
                width: 48,
                align: 'center'
              },
              {
                prop: 'username',
                label: '账号',
                align: 'center',
                sortable: 'custom'
              },
              {
                prop: 'nickname',
                label: '用户名',
                align: 'center',
                sortable: 'custom'
              },
              {
                prop: 'sexName',
                label: '性别',
                align: 'center',
                sortable: 'custom'
              }
            ],
            highlightCurrentRow: true,
            style: {},
            border: false
          },
          itemProps: {
            labelWidth: 94,
            labelPosition: 'right'
          }
        },
        {
          key: 'fhet4zrilks3vr37',
          prop: 'fe4cawuy43y5pxme',
          label: '远程数据联动',
          type: 'label',
          props: {
            size: 'md',
            strong: true,
            style: {
              borderLeft: '4px solid var(--el-color-primary)',
              lineHeight: 1,
              paddingLeft: '10px',
              margin: '42px 0 22px 0'
            }
          }
        },
        {
          key: 'fn31wgo0n9nnqpyb',
          prop: 'fxy80sbtibftdj2c',
          label: '机构',
          type: 'radio',
          required: false,
          props: {
            options:
              "/*__PRO_FORM__*/async () => {\n    const res = await httpRequest.get('/system/organization');\n    return res.data.data.map(d => ({ label: d.organizationName, value: d.organizationId }));\n}\n",
            onChange:
              "/*__PRO_FORM__*/(value) => {\n    form.f4g1toqz8p51675j = void 0;\n    getProFormRefs()['f4g1toqz8p51675jRef']?.reloadOptions?.();\n}"
          },
          itemProps: {
            labelWidth: 56
          }
        },
        {
          key: 'fzxvjg87g103rgec',
          prop: 'f1s1irhe7w8re7in',
          label: '选择上面机构后会筛选下面用户数据',
          type: 'label',
          required: false,
          props: {}
        },
        {
          key: 'f0dkysx2wn7rocmu',
          prop: 'f4g1toqz8p51675j',
          label: '用户',
          type: 'checkbox',
          required: false,
          props: {
            options:
              "/*__PRO_FORM__*/async () => {\n    const res = await httpRequest.get('/system/user', {\n        params: { organizationId: form.fxy80sbtibftdj2c }\n    });\n    return res.data.data.map(d => ({\n        label: `${d.nickname}(${d.organizationName})`,\n        value: d.userId\n    }));\n}"
          },
          itemProps: {
            labelWidth: 56
          }
        }
      ]
    }
  }
];
