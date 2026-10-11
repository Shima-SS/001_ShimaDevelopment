<?php
/**
 * 確認用の最小ループ。get_header() 等のテンプレートタグは使わず、
 * 投稿タイトル（リンク付き）と投稿タイプ名のみを表示する。
 */

defined( 'ABSPATH' ) || exit;
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php if ( have_posts() ) : ?>
	<?php while ( have_posts() ) : the_post(); ?>
		<p>
			<a href="<?php echo esc_url( get_permalink() ); ?>"><?php echo esc_html( get_the_title() ); ?></a>
			（<?php echo esc_html( get_post_type() ); ?>）
		</p>
	<?php endwhile; ?>
<?php endif; ?>
<?php wp_footer(); ?>
</body>
</html>
