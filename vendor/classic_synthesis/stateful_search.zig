// stateful_search.zig - MALDOOM local search for stateful Classic programs.
// Runs one program with a SEQUENCE of inputs and checks the FULL output sequence.
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
    if (args.len < 4) {
        std.debug.print("usage: stateful_search <length> <max_steps> <input_seq> [EMIT <path>]\n", .{});
        std.debug.print("  input_seq: e.g. \"012\" (three inputs)\n", .{});
        std.debug.print("  Searches for program producing 3+ distinct output chars.\n", .{});
        std.process.exit(2);
    }
    const length = try std.fmt.parseInt(usize, args[1], 10);
    const max_steps = try std.fmt.parseInt(u32, args[2], 10);
    const input_seq = args[3];
    var emit_path: []const u8 = "";
    if (args.len >= 6 and std.mem.eql(u8, args[4], "EMIT")) emit_path = args[5];
    var chars: [16][8]u8 = undefined;
    var cells: [16]u32 = undefined;
    var idx: [16]u8 = [_]u8{0} ** 16;
    for (0..length) |pos| {
        for (ops, 0..) |op, k| chars[pos][k] = validCharAt(pos, op);
        cells[pos] = chars[pos][0];
    }
    vm.buildCrazy5();
    const total = std.math.pow(u64, 8, @intCast(length));
    var hits: u64 = 0;
    var n: u64 = 0;
    while (n < total) : (n += 1) {
        // Run ONCE with the full input sequence
        const outcome = vm.runProgram(cells[0..length], input_seq, max_steps);
        const output = vm.out_buf[0..outcome.output_len];
        // Check if output has at least 3 chars and first 3 are all different
        if (output.len >= 3 and output[0] != output[1] and output[1] != output[2] and output[0] != output[2]) {
            // Count all, but flag long-running ones
            if (outcome.steps >= 20 and !outcome.terminated) {
                hits += 1;
                for (0..length) |pos| std.debug.print("{c}", .{chars[pos][idx[pos]]});
                std.debug.print(" LONG steps={d} output_len={d} output=\"{s}\" terminated={s}\n", .{outcome.steps, output.len, output, if (outcome.terminated) "yes" else "no"});
            } else if (outcome.steps >= 20) {
                hits += 1;
                for (0..length) |pos| std.debug.print("{c}", .{chars[pos][idx[pos]]});
                std.debug.print(" steps={d} output_len={d} output=\"{s}\" terminated={s}\n", .{outcome.steps, output.len, output, if (outcome.terminated) "yes" else "no"});
            }
            if (emit_path.len > 0) {
                var prog_str = std.ArrayList(u8).empty;
                for (0..length) |pos| try prog_str.append(alloc, chars[pos][idx[pos]]);
                const json = std.fmt.allocPrint(alloc, "{{\"program\":\"{s}\",\"length\":{d},\"input_seq\":\"{s}\",\"output\":\"{s}\",\"steps\":{d},\"terminated\":{s}}}",
                    .{prog_str.items, length, input_seq, output, outcome.steps, if (outcome.terminated) "true" else "false"}) catch unreachable;
                prog_str.deinit(alloc);
                defer alloc.free(json);
                const file = try std.Io.Dir.createFileAbsolute(init.io, emit_path, .{});
defer file.close(init.io);
try file.writeStreamingAll(init.io, json);
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
    std.debug.print("STATEFUL total={d} hits={d} input_seq={s}\n", .{ total, hits, input_seq });
}
