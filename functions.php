<?php
/**
 * テーマの読み込みエントリーポイント。inc/ 配下の各ファイルを require するだけ。
 */

defined( 'ABSPATH' ) || exit;

require_once get_template_directory() . '/inc/setup.php';
require_once get_template_directory() . '/inc/enqueue.php';
