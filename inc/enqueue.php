<?php
/**
 * Google Fonts と style.css / tokens.css の読み込み。
 */

defined( 'ABSPATH' ) || exit;

function shima_enqueue_assets() {
	wp_enqueue_style(
		'shima-google-fonts',
		'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap',
		array(),
		null
	);

	wp_enqueue_style(
		'shima-tokens',
		get_template_directory_uri() . '/assets/css/tokens.css',
		array(),
		filemtime( get_template_directory() . '/assets/css/tokens.css' )
	);

	wp_enqueue_style(
		'shima-style',
		get_stylesheet_uri(),
		array( 'shima-tokens' ),
		filemtime( get_template_directory() . '/style.css' )
	);
}
add_action( 'wp_enqueue_scripts', 'shima_enqueue_assets' );

function shima_resource_hints( $urls, $relation_type ) {
	if ( 'preconnect' === $relation_type ) {
		$urls[] = array(
			'href' => 'https://fonts.googleapis.com',
		);
		$urls[] = array(
			'href'        => 'https://fonts.gstatic.com',
			'crossorigin' => 'anonymous',
		);
	}
	return $urls;
}
add_filter( 'wp_resource_hints', 'shima_resource_hints', 10, 2 );
