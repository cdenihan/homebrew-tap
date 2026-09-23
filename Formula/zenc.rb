class Zenc < Formula
  desc "Systems language compiling to readable C"
  homepage "https://www.zenc-lang.org/"
  url "https://github.com/zenc-lang/zenc/releases/download/v0.4.4/zc.com"
  sha256 "e6f7a91321daacadc838e709f734fa3a039ed1a545e63d2b911949c4fa02eed0"
  license "MIT"

  depends_on :macos

  # Homebrew cannot identify the APE binaries as executable during cleanup.
  skip_clean "bin/zc", "bin/zc-boot"

  resource "zc-boot" do
    url "https://github.com/zenc-lang/zenc/releases/download/v0.4.4/zc-boot.com"
    sha256 "2fe1d2857df506053054004991574a9e712d87a351e848bc3b0367584688c53e"
  end

  def install
    chmod 0755, "zc.com"
    bin.install "zc.com" => "zc"

    resource("zc-boot").stage do
      chmod 0755, "zc-boot.com"
      bin.install "zc-boot.com" => "zc-boot"
    end
  end

  test do
    assert_match "zc v#{version}", shell_output("#{bin}/zc --version")
    assert_predicate bin/"zc-boot", :executable?
    (testpath/"hello.zc").write <<~ZC
      fn main() {
        println "hello from Zen C";
      }
    ZC
    assert_match "hello from Zen C", shell_output("#{bin}/zc run hello.zc 2>&1")
  end
end
