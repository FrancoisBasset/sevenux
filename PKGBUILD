pkgname=sevenux
pkgver=0.0.1
pkgrel=1
pkgdesc="Fast-paced terminal card game inspired by Flip 7"
arch=('any')
license=('MIT')
depends=('python>=3.14' 'python-readchar')
makedepends=('python-build' 'python-installer' 'python-wheel')

build() {
  cd "$startdir"
  rm -rf dist build *.egg-info

  python -m build --wheel --no-isolation
}

package() {
  cd "$startdir"

  python -m installer --destdir="$pkgdir" dist/*.whl
}