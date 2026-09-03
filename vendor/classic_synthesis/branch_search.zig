// Local MALDOOM multi-case Classic searcher. Uses the vendored Autobolge VM.
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
    if (args.len < 7 or args.len % 2 == 0) {
        std.debug.print("usage: branch_search <length> <max_steps> <input1> <output1> [<inputN> <outputN> ...]\n", .{});
        std.process.exit(2);
    }
    const length = try std.fmt.parseInt(usize, args[1], 10);
    const max_steps = try std.fmt.parseInt(u32, args[2], 10);
    if (length == 0 or length > 16) return error.InvalidLength;
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
        var matched = true;
        var arg: usize = 3;
        while (arg < args.len) : (arg += 2) {
            const outcome = vm.runProgram(cells[0..length], args[arg], max_steps);
            if (!std.mem.eql(u8, vm.out_buf[0..outcome.output_len], args[arg + 1])) {
                matched = false;
                break;
            }
        }
        if (matched) {
            hits += 1;
            for (0..length) |pos| std.debug.print("{c}", .{chars[pos][idx[pos]]});
            std.debug.print(" matches={d}\n", .{(args.len - 3) / 2});
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
    std.debug.print("BRANCH total={d} hits={d}\n", .{ total, hits });
}
