#include <cassert>
#include <iostream>
#include <filesystem>
#include <print>
#include <fstream>
#include <ranges>
#include <algorithm>
#include <iterator>

// Inspired by Tsoding: https://github.com/rexim/tore/blob/main/src_build/tt.c

void compile_cpp_code(std::ostream &out, std::string_view s)
{
	out << s << "\n";
}

void compile_byte_array(std::ostream &out, std::string_view s)
{
	// TODO: Escaping
	out << "out(R\"ttstring(" << s << ")ttstring\");\n";
}

int main(int argc, char **argv)
{
	auto program_name = std::filesystem::path(argv[0]).filename();
	if (argc < 2) {
		std::print(stderr, "usage: {} <filename.hh.tt>\n", program_name.c_str());
		return 2;
	}

	std::string input_path = argv[1];
	assert(input_path.ends_with(".tt"));

	std::string output_path = input_path;
	output_path.erase(output_path.size() - 3);

	std::ifstream input(input_path);
	assert(input.is_open());
	std::string sourcebuf{std::istreambuf_iterator<char>(input), {}};

	std::ofstream output(output_path);
	assert(output.is_open());

	bool cpp_code_mode = false;
	std::string_view source{sourcebuf};

	// TODO: Generate line control preprocessor directives
	// - GCC: https://gcc.gnu.org/onlinedocs/cpp/Line-Control.html
	while (source.size()) {
		std::string_view token = source;
		if (auto sep = source.find('@'); sep != std::string_view::npos) {
			token = token.substr(0, sep);
			source = source.substr(sep + 1);
		} else {
			source = {};
		}

		if (cpp_code_mode) {
			compile_cpp_code(output, token);
		} else {
			compile_byte_array(output, token);
		}
		cpp_code_mode = !cpp_code_mode;
	}
}
