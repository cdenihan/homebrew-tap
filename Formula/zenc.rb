class Zenc < Formula
  desc "Systems language compiling to readable C"
  homepage "https://www.zenc-lang.org/"
  url "https://github.com/zenc-lang/zenc/releases/download/v0.4.4/zc.com"
  sha256 "e6f7a91321daacadc838e709f734fa3a039ed1a545e63d2b911949c4fa02eed0"
  license "MIT"

  depends_on :macos

  def install
    bin.install "zc.com" => "zc"
    chmod 0755, bin/"zc"
  end

  test do
    assert_match "zc v#{version}", shell_output("#{bin}/zc --version")
    (testpath/"hello.zc").write <<~ZC
      fn main() {
        println "hello from Zen C";
      }
    ZC
    assert_match "hello from Zen C", shell_output("#{bin}/zc run hello.zc 2>&1")
  end
end
