--数据库名称：zt_platform
--表名称：sys_sms_code
--说明：短信验证码记录表，用于验证码登录和验证码重置密码。
--      暂不接入三方短信通道，验证码生成后仅落表，通过查数据库获取验证码完成验证。
CREATE TABLE `sys_sms_code` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '手机号',
  `code` varchar(6) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '验证码（6位数字）',
  `purpose` smallint NOT NULL COMMENT '用途 1-验证码登录 2-重置密码',
  `status` smallint NOT NULL DEFAULT '0' COMMENT '状态 0-未使用 1-已使用 2-已过期',
  `expire_at` datetime NOT NULL COMMENT '过期时间',
  `client_ip` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '请求IP',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_phone_purpose` (`phone`,`purpose`,`status`,`expire_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='短信验证码表';
