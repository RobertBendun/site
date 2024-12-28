#define NOB_IMPLEMENTATION
#include "nob.h"

int main(int argc, char **argv)
{
	NOB_GO_REBUILD_URSELF(argc, argv);

	Nob_Cmd cmd = {};

	nob_cmd_append(&cmd, "c++", "-std=c++23", "-Wall", "-Wextra", "-o", "tt", "tt.cc");
	if (nob_needs_rebuild1("tt", "tt.cc")) if (!nob_cmd_run_sync(cmd)) {
		nob_log(NOB_ERROR, "failed to compile tt.cc");
	}


	cmd.count = 0;
	nob_cmd_append(&cmd, "./tt", "sitcoms.hh.tt");
	char const* deps[] = { "tt", "sitcoms.hh.tt" };
	if (nob_needs_rebuild("sitcoms.hh", deps, NOB_ARRAY_LEN(deps))) if (!nob_cmd_run_sync(cmd)) {
		nob_log(NOB_ERROR, "failed to compile sitcoms.hh");
	}

	// TODO: Use pkg-config
	cmd.count = 0;
	nob_cmd_append(&cmd, "c++", "-std=c++23", "-Wall", "-Wextra", "-o", "gen", "gen.cc", "-llowdown", "-lm", "-fconcepts-diagnostics-depth=2");

	char const* deps2[] = { "gen.cc", "sitcoms.hh" };
	if (nob_needs_rebuild("gen", deps2, NOB_ARRAY_LEN(deps2))) if (!nob_cmd_run_sync(cmd)) {
		nob_log(NOB_ERROR, "failed to compile gen.cc");
		return 1;
	}

	cmd.count = 0;
	nob_cmd_append(&cmd, "./gen");
	if (!nob_cmd_run_sync(cmd)) {
		nob_log(NOB_ERROR, "failed to run gen");
		return 1;
	}

	return 0;
}
