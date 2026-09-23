class Xfer < Formula
  desc "Secure file and directory transfer over a direct TCP connection"
  homepage "https://github.com/cdenihan/XFER"
  url "https://github.com/cdenihan/XFER/releases/download/v2026.09.06.1/VERSION"
  sha256 "ba12030f8bffa60e746fb6fd0f668b067bb4fa3bc5e00d05b1142f9f74c2af83"

  depends_on :macos

  resource "binary" do
    on_arm do
      url "https://github.com/cdenihan/XFER/releases/download/v2026.09.06.1/xfer-macos-aarch64"
      sha256 "2867d829032943b234a2942f34b619e8eee524b1eef96be3dd955655bd32259c"
    end

    on_intel do
      url "https://github.com/cdenihan/XFER/releases/download/v2026.09.06.1/xfer-macos-x86_64"
      sha256 "0354c97afbaf7120d4097c78cbbf9582c0412e8db90f5933da8b864f2f783eba"
    end
  end

  def install
    resource("binary").stage do
      binary = Dir["xfer-macos-*"].fetch(0)
      chmod 0755, binary
      bin.install binary => "xfer"
    end
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/xfer --version")
  end
end
