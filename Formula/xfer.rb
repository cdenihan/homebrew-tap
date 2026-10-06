class Xfer < Formula
  desc "Secure file and directory transfer over a direct TCP connection"
  homepage "https://github.com/cdenihan/XFER"
  url "https://github.com/cdenihan/XFER/releases/download/v2.0.1/VERSION"
  sha256 "fe840f52fb5578d3f77eb497115eb02c6036601c3a53e60df7995c7276baa77a"

  depends_on :macos

  resource "binary" do
    on_arm do
      url "https://github.com/cdenihan/XFER/releases/download/v2.0.1/xfer-2.0.1-aarch64-macos.tar.gz"
      sha256 "509e2bb8749d49f2b5c48e4b76533d2368dfd05d41bfdc4cb260f18d9aa6cea5"
    end

    on_intel do
      url "https://github.com/cdenihan/XFER/releases/download/v2.0.1/xfer-2.0.1-x86_64-macos.tar.gz"
      sha256 "e4b6ba2f2ec61c1f7a931c271b01e160ffbfe8e171897308504c335856012f51"
    end
  end

  def install
    resource("binary").stage do
      binary = Dir["xfer", "xfer-macos-*"].fetch(0)
      chmod 0755, binary
      bin.install binary => "xfer"
    end
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/xfer --version")
  end
end
