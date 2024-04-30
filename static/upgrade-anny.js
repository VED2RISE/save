function sortBy(field) {
  const url = new URL(window.location);
  url.searchParams.set('sort_by', field);  // 设置排序字段
  url.searchParams.set('order', field === url.searchParams.get('sort_by') && url.searchParams.get('order') === 'desc' ? 'asc' : 'desc');  // 切换排序顺序
  window.location.href = url.href;  // 重定向到新的URL
}

function restoreDefault() {
  const url = new URL(window.location);
  url.searchParams.delete('sort_by');
  url.searchParams.delete('order');
  window.location.href = url.href;
}