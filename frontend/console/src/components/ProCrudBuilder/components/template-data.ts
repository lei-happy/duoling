import { markRaw } from 'vue';
import type { TemplateItem } from 'ele-admin-plus/es/ele-crud-builder/types';
import CoverBasic from './template-covers/cover-basic.vue';
import CoverAdvanced from './template-covers/cover-advanced.vue';
import CoverTree from './template-covers/cover-tree.vue';
import CoverSplit from './template-covers/cover-split.vue';

/**
 * 模板库数据
 */
export const defaultTemplateData: TemplateItem[] = [
  {
    name: '基础列表',
    cover: markRaw(CoverBasic),
    config: {
      fields: [
        {
          key: 'f3bm9f9888k4kol8',
          prop: 'username',
          label: '用户账号',
          columnProps: { sortable: 'custom' },
          addItemProps: { required: true },
          editItemProps: { required: true }
        },
        {
          key: 'fubnc9dhl3s46dci',
          prop: 'nickname',
          label: '用户名',
          columnProps: { sortable: 'custom' },
          addItemProps: { required: true },
          editItemProps: { required: true }
        },
        {
          key: 'frsoa6vjkd002soj',
          prop: 'sexName',
          label: '性别',
          columnProps: { width: 100, align: 'center', sortable: 'custom' },
          addItemProps: {
            required: true,
            prop: 'sex',
            type: 'dictRadio',
            props: { code: 'sex' }
          },
          editItemProps: {
            required: true,
            prop: 'sex',
            type: 'dictRadio',
            props: { code: 'sex' }
          }
        },
        {
          key: 'fkndbwy5yucoxb5d',
          prop: 'createTime',
          label: '创建时间',
          hideInSearch: true,
          hideInAdd: true,
          hideInEdit: true,
          columnProps: { align: 'center', sortable: 'custom' }
        }
      ],
      listApi:
        "/*__PRO_CRUD__*/async ({ pages, where, orders }) => {\n    const res = await httpRequest.get('/system/user/page', {\n        params: Object.assign({}, where, orders, pages)\n    });\n    if (res.data.code === 0) {\n        return res.data.data;\n    }\n    return Promise.reject(new Error(res.data.message));\n}",
      deleteApi:
        "/*__PRO_CRUD__*/async (dataKeys) => {\n    const res = await httpRequest.delete('/system/user/batch', {\n        data: dataKeys\n    });\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      addApi:
        "/*__PRO_CRUD__*/async (data) => {\n    const res = await httpRequest.post('/system/user', data);\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      editApi:
        "/*__PRO_CRUD__*/async (data) => {\n    const res = await httpRequest.put('/system/user', data);\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      searchConfig: { cardProps: true },
      listConfig: {
        cardProps: { bodyStyle: { paddingTop: '8px' } },
        tableProps: { rowKey: 'userId', showOverflowTooltip: true }
      },
      pageConfig: { pageProps: true }
    }
  },
  {
    name: '复杂表头',
    cover: markRaw(CoverAdvanced),
    config: {
      fields: [
        {
          key: 'f15itx5juqgtyqor',
          prop: 'username',
          label: '用户账号',
          columnProps: { align: 'center', sortable: 'custom' },
          addItemProps: { required: true },
          editItemProps: { required: true }
        },
        {
          key: 'f8dqe9k30w6l6sm3',
          prop: 'nickname',
          label: '用户名',
          columnProps: { align: 'center', sortable: 'custom' },
          addItemProps: { required: true },
          editItemProps: { required: true }
        },
        {
          key: 'f6u8d3tvczoo5tck',
          prop: 'basicInfo',
          label: '基本信息',
          columnProps: { align: 'center' },
          hideInSearch: 'flat',
          hideInAdd: 'flat',
          hideInEdit: 'flat',
          children: [
            {
              key: 'f52i8gr6xedlyrxg',
              prop: 'sexName',
              label: '性别',
              columnProps: { width: 100, align: 'center', sortable: 'custom' },
              addItemProps: {
                required: true,
                prop: 'sex',
                type: 'dictRadio',
                props: { code: 'sex' }
              },
              editItemProps: {
                required: true,
                prop: 'sex',
                type: 'dictRadio',
                props: { code: 'sex' }
              }
            },
            {
              key: 'f08dwkuscdzrg2hv',
              prop: 'phone',
              label: '手机号',
              columnProps: { align: 'center', sortable: 'custom' },
              searchItemProps: { vIf: 'searchExpand' }
            },
            {
              key: 'fl0a5i9wmfywj63m',
              prop: 'organizationName',
              label: '部门',
              columnProps: { align: 'center', sortable: 'custom' },
              searchItemProps: { vIf: 'searchExpand' }
            }
          ]
        },
        {
          key: 'fult8ssfpsysczl7',
          prop: 'createTime',
          label: '创建时间',
          hideInSearch: true,
          hideInAdd: true,
          hideInEdit: true,
          columnProps: { align: 'center', sortable: 'custom' }
        }
      ],
      listApi:
        "/*__PRO_CRUD__*/async ({ pages, where, orders }) => {\n    const res = await httpRequest.get('/system/user/page', {\n        params: Object.assign({}, where, orders, pages)\n    });\n    if (res.data.code === 0) {\n        return res.data.data;\n    }\n    return Promise.reject(new Error(res.data.message));\n}",
      deleteApi:
        "/*__PRO_CRUD__*/async (dataKeys) => {\n    const res = await httpRequest.delete('/system/user/batch', {\n        data: dataKeys\n    });\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      addApi:
        "/*__PRO_CRUD__*/async (data) => {\n    const res = await httpRequest.post('/system/user', data);\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      editApi:
        "/*__PRO_CRUD__*/async (data) => {\n    const res = await httpRequest.put('/system/user', data);\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      searchConfig: {
        cardProps: true,
        formProps: { showSearchExpand: true }
      },
      listConfig: {
        cardProps: { bodyStyle: { paddingTop: '8px' } },
        tableProps: { rowKey: 'userId', showOverflowTooltip: true }
      },
      pageConfig: { pageProps: true }
    }
  },
  {
    name: '树形列表',
    cover: markRaw(CoverTree),
    config: {
      fields: [
        {
          key: 'fzy9xxkozygila3e',
          prop: 'parentId',
          label: '上级机构',
          addItemProps: {
            type: 'treeSelect',
            props: {
              defaultExpandAll: true,
              nodeKey: 'organizationId',
              props: { label: 'organizationName' },
              data: "/*__PRO_FORM__*/async () => {\n    const res = await httpRequest.get('/system/organization/tree');\n    return res.data.data;\n}"
            }
          },
          editItemProps: {
            type: 'treeSelect',
            props: {
              defaultExpandAll: true,
              nodeKey: 'organizationId',
              props: { label: 'organizationName' },
              data: "/*__PRO_FORM__*/async () => {\n    const res = await httpRequest.get('/system/organization/tree');\n    return res.data.data;\n}"
            }
          },
          hideInList: true,
          hideInSearch: true
        },
        {
          key: 'f6buzjg5wno9lxsx',
          prop: 'organizationName',
          label: '机构名称',
          columnProps: { minWidth: 160, sortable: 'custom' },
          addItemProps: { required: true },
          editItemProps: { required: true }
        },
        {
          key: 'fv7nvwq95idzcje2',
          prop: 'organizationTypeName',
          label: '机构类型',
          columnProps: { align: 'center', minWidth: 100 },
          addItemProps: {
            required: true,
            prop: 'organizationType',
            type: 'dictSelect',
            props: { code: 'organization_type' }
          },
          editItemProps: {
            required: true,
            prop: 'organizationType',
            type: 'dictSelect',
            props: { code: 'organization_type' }
          }
        },
        {
          key: 'fkuq8hm3kzmnt29t',
          prop: 'sortNumber',
          label: '排序号',
          columnProps: { align: 'center', minWidth: 100 },
          addItemProps: { required: true, type: 'inputNumber' },
          editItemProps: { required: true, type: 'inputNumber' },
          hideInSearch: true
        },
        {
          key: 'fgy01h6mmxmzdotf',
          prop: 'createTime',
          label: '创建时间',
          hideInSearch: true,
          hideInAdd: true,
          hideInEdit: true,
          columnProps: { align: 'center', width: 180, sortable: 'custom' }
        },
        {
          key: 'fng15so67wb4d8r8',
          prop: 'comments',
          label: '备注',
          addItemProps: { type: 'textarea' },
          editItemProps: { type: 'textarea' },
          hideInList: true,
          hideInSearch: true
        }
      ],
      listApi:
        "/*__PRO_CRUD__*/async ({ where, orders }) => {\n    const res = await httpRequest.get('/system/organization/tree', {\n        params: Object.assign({}, where, orders)\n    });\n    if (res.data.code === 0) {\n        return res.data.data;\n    }\n    return Promise.reject(new Error(res.data.message));\n}",
      deleteApi:
        "/*__PRO_CRUD__*/async (dataKeys) => {\n    const res = await httpRequest.delete('/system/organization/batch', {\n        data: dataKeys\n    });\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}",
      addApi:
        "/*__PRO_CRUD__*/async (data) => {\n    const res = await httpRequest.post('/system/organization', data);\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}",
      editApi:
        "/*__PRO_CRUD__*/async (data) => {\n    const res = await httpRequest.put('/system/organization', data);\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}",
      searchConfig: { cardProps: true },
      listConfig: {
        cardProps: { bodyStyle: { paddingTop: '8px' } },
        tableProps: {
          rowKey: 'organizationId',
          showOverflowTooltip: true,
          defaultExpandAll: true,
          pagination: false
        },
        selectionColumnProps: false,
        delBtnProps: false
      },
      pageConfig: { pageProps: true }
    }
  },
  {
    name: '左树右表',
    cover: markRaw(CoverSplit),
    config: {
      fields: [
        {
          key: 'ftva2ignsk7s9t4v',
          prop: 'organizationId',
          label: '所属机构',
          addItemProps: {
            type: 'treeSelect',
            props: {
              defaultExpandAll: true,
              nodeKey: 'organizationId',
              props: { label: 'organizationName' },
              data: "/*__PRO_FORM__*/async () => {\n    const res = await httpRequest.get('/system/organization/tree');\n    return res.data.data;\n}"
            }
          },
          editItemProps: {
            type: 'treeSelect',
            props: {
              defaultExpandAll: true,
              nodeKey: 'organizationId',
              props: { label: 'organizationName' },
              data: "/*__PRO_FORM__*/async () => {\n    const res = await httpRequest.get('/system/organization/tree');\n    return res.data.data;\n}"
            }
          },
          hideInList: true,
          hideInSearch: true
        },
        {
          key: 'f3r9kb783l24qpit',
          prop: 'username',
          label: '用户账号',
          columnProps: { sortable: 'custom' },
          addItemProps: { required: true },
          editItemProps: { required: true }
        },
        {
          key: 'fxy1ea06rvv14qkg',
          prop: 'nickname',
          label: '用户名',
          columnProps: { sortable: 'custom' },
          addItemProps: { required: true },
          editItemProps: { required: true }
        },
        {
          key: 'feh00v74vjp8wzbc',
          prop: 'sexName',
          label: '性别',
          columnProps: { width: 100, align: 'center', sortable: 'custom' },
          addItemProps: {
            required: true,
            prop: 'sex',
            type: 'dictRadio',
            props: { code: 'sex' }
          },
          editItemProps: {
            required: true,
            prop: 'sex',
            type: 'dictRadio',
            props: { code: 'sex' }
          }
        },
        {
          key: 'f2f5l2luqhpca0a2',
          prop: 'createTime',
          label: '创建时间',
          hideInSearch: true,
          hideInAdd: true,
          hideInEdit: true,
          columnProps: { align: 'center', sortable: 'custom' }
        }
      ],
      listApi:
        "/*__PRO_CRUD__*/async ({ pages, where, orders }) => {\n    const res = await httpRequest.get('/system/user/page', {\n        params: Object.assign({}, where, orders, pages)\n    });\n    if (res.data.code === 0) {\n        return res.data.data;\n    }\n    return Promise.reject(new Error(res.data.message));\n}",
      deleteApi:
        "/*__PRO_CRUD__*/async (dataKeys) => {\n    const res = await httpRequest.delete('/system/user/batch', {\n        data: dataKeys\n    });\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      addApi:
        "/*__PRO_CRUD__*/async (data) => {\n    const res = await httpRequest.post('/system/user', data);\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      editApi:
        "/*__PRO_CRUD__*/async (data) => {\n    const res = await httpRequest.put('/system/user', data);\n    if (res.data.code === 0) {\n        return res.data.message;\n    }\n    return Promise.reject(new Error(res.data.message));\n}\n",
      treeListApi:
        "/*__PRO_CRUD__*/async () => {\n    const res = await httpRequest.get('/system/organization/tree');\n    if (res.data.code === 0) {\n        return res.data.data;\n    }\n    return Promise.reject(new Error(res.data.message));\n}",
      searchConfig: { cardProps: false },
      listConfig: {
        cardProps: false,
        tableProps: { rowKey: 'userId', showOverflowTooltip: true }
      },
      pageConfig: {
        splitPanelProps: { flexTable: 'auto' },
        splitSearchForm: true,
        cardProps: {
          flexTable: 'auto',
          bodyStyle: { padding: '0' }
        },
        pageProps: { flexTable: true },
        tableFilterField: 'organizationId',
        sideConfig: {
          treeProps: {
            nodeKey: 'organizationId',
            props: { label: 'organizationName' }
          }
        }
      }
    }
  }
];
