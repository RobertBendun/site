#include <cassert>
#include <cctype>
#include <set>
#include <sys/queue.h>
#include <string_view>
#include <cstdio>
#include <iostream>
#include <filesystem>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <optional>
#include <ranges>
#include <algorithm>
#include <print>
#include <generator>

#include <lowdown.h>

static std::string program_name;

struct Date
{
	std::chrono::year year;
	std::optional<std::chrono::month> month;
};

template<typename T>
struct inclusive_range
{
	T from, to;

	using value_type = T;
	using difference_type = std::ptrdiff_t;
	using iterator_category = std::forward_iterator_tag;

	constexpr inclusive_range begin() const { return *this; }
	constexpr inclusive_range end() const { auto end = to; return { .from = ++end, .to = to }; }

	T operator*() const { return from; }
	inclusive_range& operator++() { ++from; return *this; }
	inclusive_range operator++(int) { return { .from = from++, .to = to }; }

	bool operator==(inclusive_range<T> const&) const = default;
	auto operator<=>(inclusive_range<T> const&) const = default;

	bool contains(T const& rhs)
	{
		return from <= rhs && rhs <= to;
	}
};

static_assert(std::forward_iterator<inclusive_range<int>>);
static_assert(std::ranges::forward_range<inclusive_range<int>>);

using Seasons = std::vector<inclusive_range<std::chrono::year>>;

struct Series
{
	std::string path;
	std::string_view title;
	std::string_view review;

	std::string_view watched, network;

	Seasons seasons;
	std::vector<std::string> tags;

	static Series from_file(char const* path);
	void dump();

	inclusive_range<std::chrono::year> bounds() const
	{
		assert(seasons.size());
		return {seasons.front().from, seasons.back().to};
	}

	auto operator<=>(Series const& other) const
	{
		assert(seasons.size());
		assert(other.seasons.size());

		if (auto cmp = bounds() <=> other.bounds(); cmp == 0) {
			return title <=> other.title;
		} else {
			return cmp;
		}
	}
};

Seasons parse_seasons_declaration(std::string_view s)
{
	std::size_t expected_number = 1;
	std::size_t number;
	enum {
		SEASON_NUMBER,
		YEAR_RANGE,
	} state;

	Seasons seasons;

	while (s.size()) {
		while (s.size() && std::isspace(s.front())) s.remove_prefix(1);
		if (s.empty()) break;

		auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), number);
		assert(ec == std::errc{}); // TODO: Implement better error handling
		s = { p, s.data() + s.size() };

		switch (state) {
		break; case SEASON_NUMBER: {
			assert(expected_number == number); // TODO: error handling
			++expected_number;
			state = YEAR_RANGE;
		}
		break; case YEAR_RANGE: {
			auto &year = seasons.emplace_back();
			year.from = std::chrono::year(number);
			if (s.starts_with("..")) {
				s.remove_prefix(2);
				auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), number);
				assert(ec == std::errc{}); // TODO: Implement better error handling
				s = { p, s.data() + s.size() };
				year.to = std::chrono::year(number);
			} else {
				year.to = year.from;
			}
			state = SEASON_NUMBER;
		}
		}
	}

	assert(state == SEASON_NUMBER);

	return seasons;
}

Series Series::from_file(char const* path)
{
	Series series;
	series.path = path;

	struct lowdown_opts opts = {};
	opts.type = LOWDOWN_HTML;
	opts.feat = LOWDOWN_COMMONMARK
		        | LOWDOWN_FENCED
						| LOWDOWN_AUTOLINK
						| LOWDOWN_METADATA;
	opts.oflags = LOWDOWN_HTML_HEAD_IDS;

	struct lowdown_metaq mq = {}; // Don't deallocate since it's field are later used
	struct lowdown_meta *m;
	TAILQ_INIT(&mq);

	char *ret = NULL; // Don't deallocate since it's used later to store review
	size_t retsz = 0;

	std::unique_ptr<FILE, int(*)(FILE*)> source(fopen(path, "r"), fclose);

	if (!lowdown_file(&opts, source.get(), &ret, &retsz, &mq)) {
		std::cerr << program_name << ": error: failed to render markdown for " << path << "\n";
		exit(1);
	}

	TAILQ_FOREACH(m, &mq, entries) {
		std::string_view key = m->key;
		if (0) {}
		else if (key == "title")   { series.title   = m->value; }
		else if (key == "tags") {
			std::string next;
			for (std::istringstream ss{m->value}; ss >> next;) {
				series.tags.push_back(next);
			}
		}
		else if (key == "watched") { series.watched = m->value; }
		else if (key == "seasons") {
			series.seasons = parse_seasons_declaration(m->value);
		}
		else if (key == "network") { series.network = m->value; }
		else {
			std::cerr << program_name << ": error: " << path << ": unrecognized metadata key: " << m->key << "\n";
			continue;
		}
	}

	series.review = { ret, retsz };

	return series;
}

void Series::dump()
{
	auto [min, max] = std::ranges::minmax(std::views::join(seasons));
	std::cout << title << " (" << min << "-" << max << "):";
	for (auto const& t : tags) std::cout << " #" << t;
	std::cout << '\n';
}

struct Series_Collection
{
	std::vector<std::shared_ptr<Series>> series;
	std::unordered_multimap<std::string, std::shared_ptr<Series>> tags;

	static Series_Collection from_directory(std::filesystem::path root);
};

Series_Collection Series_Collection::from_directory(std::filesystem::path root)
{
	Series_Collection s;

	for (auto d : std::filesystem::directory_iterator{root}) {
		auto p = d.path();
		s.series.emplace_back(new Series(Series::from_file(p.c_str())));
		auto &series = s.series.back();
		for (auto const& tag : series->tags) {
			s.tags.insert(std::pair{tag, series});
		}
	}

	return s;
}

int main(int, char **argv)
{
	program_name = std::filesystem::path(argv[0]).filename().string();

	auto coll = Series_Collection::from_directory("./series/");


	auto out = [](auto &&value) {
		std::cout << value;
	};

	auto [sitcom_begin, sitcom_end] = coll.tags.equal_range("sitcom");
	auto sitcoms = std::ranges::subrange(sitcom_begin, sitcom_end)
			| std::views::transform([](auto &p) -> auto& { return p.second; })
			| std::ranges::to<std::vector>();
	std::ranges::sort(sitcoms, std::less<>{}, [](auto const& x) -> auto& { return *x; });

	auto const [year_start, year_end] = std::ranges::minmax(
			sitcoms
		| std::views::transform([](auto const& s) { return s->seasons; })
		| std::views::join
		| std::views::join);

#include "sitcoms.hh"

	return 0;
}
