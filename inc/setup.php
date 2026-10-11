<?php
/**
 * テーマサポート・ナビゲーションメニュー・画像サイズの登録。
 */

defined( 'ABSPATH' ) || exit;

function shima_setup() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support(
		'html5',
		array(
			'search-form',
			'gallery',
			'caption',
			'style',
			'script',
		)
	);
	add_theme_support( 'responsive-embeds' );

	register_nav_menus(
		array(
			'primary' => __( 'グローバルメニュー', 'shima' ),
			'footer'  => __( 'フッターメニュー（SNS）', 'shima' ),
		)
	);

	add_image_size( 'shima-card', 960, 600, true );
	add_image_size( 'shima-shot', 600, 1300, false );
}
add_action( 'after_setup_theme', 'shima_setup' );
