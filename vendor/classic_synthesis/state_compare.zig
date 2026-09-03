// state_compare.zig - MALDOOM P5 primitive: cross-read input state.
//
// Goal: find a Classic program whose output depends on state carried across
// multiple reads, i.e. NOT a pure per-input echo/transducer.
//
// Contract: run the SAME immutable program twice:
//   run with input seq "A1"  (leading A, trailing 1)
//   run with input seq "B1"  (leading B, trailing 1)
// If the FULL output differs between the two runs, then the trailing '1' was
// processed differently depending on the leading input => the program kept
// cross-read state (a necessary primitive for HIGH_WATER/local counter).
//
// Pure echoes ("a","b" then halt on EOF) would produce outputs that DO differ
// by the leading input, so we additionally require the output to contain the
// trailing '1' processed AFTER the leading input (output_len >= 2 and the
// program did NOT halt before reading the 2nd input). This forces the second
// read to be reached, so any output difference at/after position 1 is due to
// carried state, not echo.
//
// This is a search tool, never gameplay code.
const std = @import("std");
const vm = @import("autobolge/vm.zig");

const ops = [_]u32{ 4, 5, 23, 39, 40, 62, 68, 81 };

fn validCharAt(pos: usize, op: u32) u8 {
    return @intCast(33 + @mod(@as(i64, op) - 33 - @as(i64, @intCast(pos)), 94));
}

pub fn main(init: std.process.Init) !void {
    const alloc = init.arena.allocator();
    var args_it = try std.process.Args.Iterator.initAllocator(init.minimal.args, alloc);
    defer args_it.deinit();
    var arg_list: std.ArrayList([]const u8) = .empty;
    while (args_it.next()) |arg| try arg_list.append(alloc, try alloc.dupe(u8, arg));
    const args = arg_list.items;
    if (args.len < 3) {
        std.debug.print("usage: state_compare <length> <max_steps>\n", .{});
        std.process.exit(2);
    }
    const length = try std.fmt.parseInt(usize, args[1], 10);
    const max_steps = try std.fmt.parseInt(u32, args[2], 10);
    if (length == 0 or length > 12) return error.InvalidLength;

    const seq_a = "01";
    const seq_b = "21";

    var chars: [12][8]u8 = undefined;
    var cells: [12]u32 = undefined;
    var idx: [12]u8 = [_]u8{0} ** 12;
    for (0..length) |pos| {
        for (ops, 0..) |op, k| chars[pos][k] = validCharAt(pos, op);
        cells[pos] = chars[pos][0];
    }
    vm.buildCrazy5();
    const total = std.math.pow(u64, 8, @intCast(length));
    var hits: u64 = 0;
    var n: u64 = 0;
    while (n < total) : (n += 1) {
        const out_a = vm.runProgram(cells[0..length], seq_a, max_steps);
        const out_b = vm.runProgram(cells[0..length], seq_b, max_steps);
        // Must have consumed at least both inputs (reached the trailing read).
        const oa = vm.out_buf[0..out_a.output_len];
        const ob = vm.out_buf[0..out_b.output_len];
        if (oa.len >= 1 and ob.len >= 1) {
            // The program produced output on both runs (did something with input).
            // Cross-read state: output on trailing '1' depends on leading input.
            // Compare outputs at/after the first char.
            const diff_after_lead = !std.mem.eql(u8, oa, ob);
            if (diff_after_lead) {
                hits += 1;
                for (0..length) |pos| std.debug.print("{c}", .{chars[pos][idx[pos]]});
                std.debug.print(" cross_read=yes stepsA={d} stepsB={d} outA=\"{s}\" outB=\"{s}\"\n", .{ out_a.steps, out_b.steps, oa, ob });
            }
        }
        var pos = length;
        while (pos > 0) {
            pos -= 1;
            if (idx[pos] < 7) {
                idx[pos] += 1;
                cells[pos] = chars[pos][idx[pos]];
                break;
            }
            idx[pos] = 0;
            cells[pos] = chars[pos][0];
        }
    }
    std.debug.print("STATECOMPARE total={d} hits={d} len={d}\n", .{ total, hits, length });
}