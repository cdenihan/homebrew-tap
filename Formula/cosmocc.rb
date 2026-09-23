class Cosmocc < Formula
  desc "Cosmopolitan C and C++ toolchain for portable executables"
  homepage "https://github.com/jart/cosmopolitan"
  url "https://github.com/jart/cosmopolitan/releases/download/4.0.2/cosmocc-4.0.2.zip"
  sha256 "85b8c37a406d862e656ad4ec14be9f6ce474c1b436b9615e91a55208aced3f44"
  license :cannot_represent

  depends_on :macos

  def install
    libexec.install Dir["*"]

    # The compiler locates its support files relative to $0. An ordinary
    # Homebrew symlink would make it search under Homebrew's global bin.
    %w[cosmocc cosmoc++].each do |command|
      (bin/command).write <<~SH
        #!/bin/sh
        unset CPATH C_INCLUDE_PATH CPLUS_INCLUDE_PATH OBJC_INCLUDE_PATH
        exec "#{libexec}/bin/#{command}" "$@"
      SH
    end
  end

  test do
    (testpath/"hello.c").write "#include <stdio.h>\nint main(void) { puts(\"hello from cosmocc\"); }\n"
    system bin/"cosmocc", "-o", "hello", "hello.c"
    assert_match "hello from cosmocc", shell_output("./hello")
  end
end
